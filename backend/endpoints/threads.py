
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from schema.message import Thread, MessageRequest, Message
from schema.response import ResponseModel
from schema.thread_response import ThreadResponse
from fastapi.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.message_utils import get_message, get_room_messages
from utils.room_utils import get_org_rooms
from utils.threads_utils import get_message_threads, add_message_to_thread_list
from utils.threads_utils import  update_thread_message as edit_thread_message
import json

router = APIRouter()


@router.post(
    "/org/{org_id}/rooms/{room_id}/messages/{message_id}/threads",
    response_model=ThreadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Message not found"},
        424: {"description": "Thread message not sent"},
    },
)
async def send_thread_message(
    org_id: str, 
    room_id: str,
    message_id: str,
    request: MessageRequest
):
    """Adds a thread to a parent message.

        Edits an existing message document in the messages database collection while
        publishing to all members of the room in the background.

        Args:
            org_id: A unique identifier of the organization.
            room_id: A unique identifier of the room.
            message_id: A unique identifier of the message that is being edited.
            request: A pydantic schema that defines the message request parameters.

        Returns:
            A dict containing data about the message that was edited.

            {
            "status": 201,
            "event": "thread_message_create",
            "room_id": "637f6f2d601ce3fc5dc738f5",
            "message_id": "63a6c075d4093d73264466c6",
            "data": {
                "sender_id": "637f6f28601ce3fc5dc738f4",
                "emojis": [],
                "richUiData": {
                "blocks": [
                    {
                    "key": "f3s6p",
                    "text": "ho ho ho I'm a thread message on christmas eve!",
                    "type": "unstyled",
                    "depth": 0,
                    "inlineStyleRanges": [],
                    "entityRanges": [],
                    "data": {}
                    }
                ],
                "entityMap": {}
                },
                "timestamp": 1669917458839,
                "thread_id": "75d6507d-836b-11ed-9fba-40234355d0d0",
                "created_at": "2022-12-24 09:15:08.019726"
            }
            }
            
        Raises:
            HTTPException [401]: You are not authorized to edit this message.
            HTTPException [404]: Message not found.
            HTTPException [424]: Message not edited.
        """
    
    response, thread_message = await add_message_to_thread_list(
                                org_id, room_id, message_id, request
                            )

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Thread message not sent",
        )

    result = {
                "status": 201,
                "event": "thread_message_create",
                "room_id": room_id,
                "message_id": message_id,
                "data": thread_message
            }   

    return JSONResponse(
        content=result,
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/org/{org_id}/rooms/{room_id}/messages/{message_id}/threads",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={424: {"detail": "ZC Core failed"}},
)
async def get_thread_messages(org_id: str, room_id: str, message_id: str):
    """
    Fetches all the thread_messages under a parent message

    Args:
        org_id (str): A unique identifier of an organization.
        room_id (str): A unique identifier of the room where messages are fetched from.

    Returns:
        A dict containing a list of message objects.
        {
            "status": "success",
            "message": "Messages retrieved",
            "data": [
                {
                "_id": "61e75bc065934b58b8e5d223",
                "created_at": "2022-02-02 17:57:02.630439",
                "edited": true,
                "emojis": [
                    {
                    "count": 1,
                    "emoji": "👹",
                    "name": "frown",
                    "reactedUsersId": [
                        "619ba4671a5f54782939d385"
                    ]
                    }
                ],
                ...
                },
                {...},
                "threads": [
                {
                    "created_at": "2021-09-30T11:23:55.065000Z",
                    "media": [],
                    "message": "string",
                    "message_id": "string",
                    "sender_id": "string"
                }
            ],
                ...
            ]
        }

    Raises:
        HTTPException [424]: Zc Core failed
    """

    response = await get_message_threads(org_id, room_id, message_id)

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Zc Core failed",
        )

    return JSONResponse(
        content=ResponseModel.success(
            data=response, message="Messages retrieved"),
        status_code=status.HTTP_200_OK,
    )


@router.put(
    "/org/{org_id}/rooms/{room_id}/messages/{message_id}/threads",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "You are not authorized to edit this message"},
        404: {"description": "Message not found"},
        424: {"description": "Message not edited"},
    },
)
async def update_threads_message(
    org_id: str,
    room_id: str,
    message_id: str,
    thread_id: str,
    request: MessageRequest,
    background_tasks: BackgroundTasks,
):
    
    message = await get_message(org_id, room_id, message_id)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    payload = request.dict(exclude_unset=True)

    edited_thread_message = await edit_thread_message(org_id, message_id, thread_id, payload, message)

    # Publish to centrifugo in the background.
    background_tasks.add_task(
        centrifugo_client.publish,
        room_id,
        Events.MESSAGE_UPDATE,
        message
    )

    return JSONResponse(
        content=ResponseModel.success(
            data=message, message="Thread Edited"),
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/org/{org_id}/member/{member_id}/threads",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={424: {"detail": "ZC Core failed"}},
)
async def get_threads(org_id: str, member_id: str, page: int = 1, size: int = 15):
    room_response = await get_org_rooms(org_id=org_id, member_id=member_id)

    if room_response == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member does not exist or Org not found"
        )

    if room_response is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Zc Core failed"
        )

    room_ids = []

    for room in room_response:
        room_ids.append(room['_id'])

    for room_id in room_ids:
        single_room_resp = await get_room_messages(org_id, room_id, page, size)
        if single_room_resp == []:
            # Room not found
            pass

        if single_room_resp is None:
            # Zc Core failed
            pass

        # Gotten Single Room

    messages_w_thread = []

    for messages in single_room_resp:
        if messages['threads'] != []:
            messages_w_thread.append(messages)

    return JSONResponse(
        content=ResponseModel.success(
            data=messages_w_thread, message="Rooms retrieved"),
        status_code=status.HTTP_200_OK,
    )
