
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from schema.message import Thread, MessageRequest, Message
from schema.response import ResponseModel
from fastapi.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.message_utils import get_message, get_room_messages
from utils.room_utils import get_org_rooms
from utils.threads_utils import get_messages_in_thread, add_message_to_thread
import json

router = APIRouter()

@router.post(
		"/org/{org_id}/rooms/{room_id}/messages/{message_id}/threads",
		response_model=ResponseModel,
		status_code=status.HTTP_201_CREATED,
		responses={
				404: {"description": "Message not found"},
				424: {"description": "Message not added to thread"},
		},
)
async def add_messages_to_thread(org_id, room_id, message_id, request: MessageRequest):
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
                    "thread": true,
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
    response = await add_message_to_thread(org_id, room_id, message_id, request)

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Zc Core failed",
        )

    return JSONResponse(
        content=ResponseModel.success(data=response, message="Messages retrieved"),
        status_code=status.HTTP_200_OK,
    )


# Get all the the messages in a thread.

@router.get(
    "/org/{org_id}/rooms/{room_id}/messages/{message_id}/threads",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={424: {"detail": "ZC Core failed"}},
)
async def get_thread_messages(org_id: str, room_id: str, message_id: str):
    """Fetches all messages sent in a particular room.

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

    response = await get_messages_in_thread(org_id, room_id, message_id )

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Zc Core failed",
        )

    return JSONResponse(
        content=ResponseModel.success(data=response, message="Messages retrieved"),
        status_code=status.HTTP_200_OK,
    )
