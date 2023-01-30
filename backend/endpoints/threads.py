from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from schema.message import MessageRequest
from schema.response import ResponseModel
from schema.thread_response import ThreadResponse
from utils.centrifugo import Events, centrifugo_client
from utils.message_utils import get_message
from utils.threads_utils import add_message_to_thread_list, get_message_threads
from utils.threads_utils import update_thread_message as edit_message_threads

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
    background_tasks: BackgroundTasks,
):

    """(Still under development) Updates a thread message in a thread in a room.

    Edits an existing message document in the messages database collection while
    publishing to all members of the room in the background.

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
                "_id": "61c3aa9478fb01b18fac1465",
                "created_at": "2021-12-22 22:38:33.075643",
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
                "files": [],
                "org_id": "619ba4671a5f54782939d384",
                "richUiData": {
                "blocks": [
                    {
                    "data": {},
                    "depth": 0,
                    "entityRanges": [],
                    "inlineStyleRanges": [],
                    "key": "eljik",
                    "text": "HI, I'm mark.. new here",
                    "type": "unstyled"
                    }
                ],
                "entityMap": {}
                },
                "room_id": "619e28c31a5f54782939d59a",
                "saved_by": [],
                "sender_id": "619ba4671a5f54782939d385",
                "text": "string",
            }

    Raises:
        HTTPException [401]: You are not authorized to edit this message.
        HTTPException [404]: Message not found.
        HTTPException [424]: Message not edited.
    """

    message = await get_message(org_id, room_id, message_id)
    payload = request.dict(exclude_unset=True)

    updated_thread_message = await edit_message_threads(
        org_id, room_id, message_id, thread_id, payload
    )

    print(updated_thread_message)

    if not updated_thread_message:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY, detail="thread not updated"
        )

    message.update(payload)

    # Publish to centrifugo in the background.
    background_tasks.add_task(
        centrifugo_client.publish, room_id, Events.MESSAGE_UPDATE, message
    )

    return JSONResponse(
        content=ResponseModel.success(data=message, message="Thread Updated"),
        status_code=status.HTTP_200_OK,
    )


# @router.get(
#     "/org/{org_id}/member/{member_id}/threads",
#     response_model=ResponseModel,
#     status_code=status.HTTP_200_OK,
#     responses={424: {"detail": "ZC Core failed"}},
# )
# async def get_threads(org_id: str, member_id: str, page: int = 1, size: int = 15):

#     room_response = await get_org_rooms(org_id=org_id, member_id=member_id)

#     if room_response == []:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Member does not exist or Org not found"
#         )

#     if room_response is None:
#         raise HTTPException(
#             status_code=status.HTTP_424_FAILED_DEPENDENCY,
#             detail="Zc Core failed"
#         )

#     room_ids = []

#     for room in room_response:
#         room_ids.append(room['_id'])

#     for room_id in room_ids:
#         single_room_resp = await get_room_messages(org_id, room_id, page, size)
#         if single_room_resp == []:
#             # Room not found
#             pass

#         if single_room_resp is None:
#             # Zc Core failed
#             pass

#         # Gotten Single Room

#     messages_w_thread = []

#     for messages in single_room_resp:
#         if messages['threads'] != []:
#             messages_w_thread.append(messages)

#     return JSONResponse(
#         content=ResponseModel.success(
#             data=messages_w_thread, message="Rooms retrieved"),
#         status_code=status.HTTP_200_OK,
#     )
