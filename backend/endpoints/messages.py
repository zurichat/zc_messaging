from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from schema.message import Message
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.db import DB
from utils.room_utils import get_room

router = APIRouter()

MESSAGE_COLLECTION = "chats"


@router.post(
    "/org/{org_id}/rooms/{room_id}/messages",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"detail": "room or sender not found"},
        424: {"detail": "ZC Core Failed"},
    },
)
async def send_message(
    org_id, room_id, request: Message, background_tasks: BackgroundTasks
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
                "room_id": "61696f43c4193ddga309dcf7",
                "sender_id": "61696f43c4133ddaa309dcf6",
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
        HTT_404_FAILED_DEPENDENCY: Sender not in room
        HTT_404_FAILED_DEPENDENCY: Room does not exist
        HTTP_424_FAILED_DEPENDENCY: "message not sent"
    """

    message_data = request.dict()
    sender_id = message_data.get("sender_id")
    room = await get_room(org_id, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not available"
        )

    if sender_id not in set(room["room_members"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="sender not a member of this room",
        )

    response = await DB.write(MESSAGE_COLLECTION, message_data)

    if response.get("status_code") != 200:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={"Message not sent": response},
        )
    response_output = {
        "message_id": response["data"]["object_id"],
        "data": message_data,
    }
    background_tasks.add_task(
        centrifugo_client.publish, room_id, Events.MESSAGE_CREATE, response_output
    )  # publish to centrifugo in the background

    return JSONResponse(
        content=ResponseModel.success(data=response_output, message="new message sent"),
        status_code=status.HTTP_201_CREATED,
    )
