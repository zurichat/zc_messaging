from fastapi import APIRouter
from fastapi import APIRouter
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from schema.message import Message, ThreadRequest
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.db import DataStorage
from utils.room_utils import get_room

router = APIRouter()

MESSAGE_COLLECTION = "chat_messages"
test_room = "61b3fb328f945e698c7eb396"

@router.post(
    "/org/{org_id}/rooms/{room_id}/sender/{sender_id}/messages",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"detail": "room or sender not found"},
        424: {"detail": "ZC Core Failed"},
    },
)
async def send_message(
    org_id, room_id, sender_id, request:ThreadRequest, background_tasks: BackgroundTasks
):
    """Creates and sends a message from one user to another.
    Registers a new document to the chats database collection.
    Returns the message info and document id if message is successfully created
    while publishing to all members of the room in the background
    Args:
        org_id (str): A unique identifier of an organisation
        request: A pydantic schema that defines the message request parameters
        room_id: A unique identifier of the room where the message is being sent to.
    Returns:
        HTTP_201_CREATED {new message sent}:
        A dict containing data about the message that was created (response_output).
            {
                "message_id": "61696f43c4133ddga309dcf6",
                "data": {
                "room_id": "61b3fb328f945e698c7eb396",
                "sender_id": "619ba4671a5f54782939d385",
                "text": "str",
                "reactions": [],
                "saved_by": [],
                "files": [],
                "is_pinned": bool = False
                "is_edited": bool = False
                "created_at": "2021-10-15T19:51:41.928908Z",
                "thread": [],
                        }
            }
    Raises:
        HTTPException [404]: Sender not in room
        HTTPException [404]: Room does not exist
        HTTPException [424]: "message not sent"
    """
    DB = DataStorage(org_id)
    message_obj = Message(**request.dict(), org_id=org_id, room_id=room_id,
                            sender_id= sender_id)
    response = await DB.write(MESSAGE_COLLECTION, message_obj.dict())

    if response.get("status_code") != 201:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={"Message not sent": response},
        )
    message_obj.message_id = response["data"]["object_id"]

    background_tasks.add_task(
        centrifugo_client.publish, room_id, Events.MESSAGE_CREATE,
    )  # publish to centrifugo in the background

    return JSONResponse(
        content=ResponseModel.success(data=message_obj.dict(), message="new message sent"),
        status_code=status.HTTP_201_CREATED,
    )