from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from schema.message import MessageRequest
from schema.response import ResponseModel
from schema.thread_response import ThreadResponse
from utils.centrifugo import Events, centrifugo_client
from utils.threads_utils import (add_message_to_thread_list,
                                 get_message_threads, update_message_thread)

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
    org_id: str, room_id: str, message_id: str, request: MessageRequest
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
            "thread_id": "bd830644-2205-11ec-9853-2ff0a732e3ef",
            "room_id": "614e1606f31a74e068e4d2e2",
            "message_id": "6155a0e6be7f31a9275a1eca",
            "data": {
                "sender_id": "61467e181ab13c00bcc15607",
                "message": "Checking out the threads",
                "created_at": "2021-09-30T15:41:45.685000Z"
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
        "data": thread_message,
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
        content=ResponseModel.success(data=response, message="Messages retrieved"),
        status_code=status.HTTP_200_OK,
    )


@router.put(
    "/org/{org_id}/rooms/{room_id}/messages/{message_id}/threads/{thread_id}",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "You are not authorized to edit this message"},
        404: {"description": "Message not found"},
        424: {"description": "Message not edited"},
    },
)
async def update_thread_message(
    org_id: str,
    room_id: str,
    message_id: str,
    thread_id: str,
    request: MessageRequest,
):

    """Updates a thread message in a thread in a room.

    Edits a thread in an existing message document in the messages database collection
    while publishing to all members of the room in the background.

    Args:
        org_id: A unique identifier of the organization.
        room_id: A unique identifier of the room.
        message_id: A unique identifier of the message that is being edited.
        thread_id: A unique identifier of the thread that is being edited.
        request: A pydantic schema that defines the message request parameters.
        background_tasks: A background task for publishing to all
                          members of the room.

    Returns:
        A dict containing data about the thread that was edited.

            {
                "status": "success",
                "message": "Thread Updated",
                "data": {
                    "sender_id": "63cb53b42009ec8a16a5774b",
                    "emojis": [],
                    "richUiData": {
                    "blocks": [
                        {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "eljik",
                        "text": "you're right about that",
                        "type": "unstyled"
                        }
                    ]
                    },
                    "files": [],
                    "saved_by": [],
                    "timestamp": 0,
                    "created_at": "2023-01-31 08:53:04.126997",
                    "edited": true,
                    "thread_id": "b39cfddc-a0a7-11ed-b15b-b8819887ed7a"
                }
            }
    Raises:
        HTTPException [401]: You are not authorized to edit this thread message.
        HTTPException [404]: Message not found.
        HTTPException [424]: thread not updated.
    """

    payload = request.dict(exclude_unset=True)

    updated_thread_message = await update_message_thread(
        org_id, room_id, message_id, thread_id, payload
    )

    if not updated_thread_message:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY, detail="thread not updated"
        )

    return JSONResponse(
        content=ResponseModel.success(data=payload, message="Thread Updated"),
        status_code=status.HTTP_200_OK,
    )
