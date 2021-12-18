from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from schema.message import Message, MessageRequest
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.db import DataStorage

router = APIRouter()

MESSAGE_COLLECTION = "messages"


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
    org_id,
    room_id,
    sender_id,
    request: MessageRequest,
    background_tasks: BackgroundTasks,
):
    """Creates and sends a message from one user to another.
    Registers a new document to the chats database collection.
    Returns the message info and document id if message is successfully created
    while publishing to all members of the room in the background
    Args:
        org_id (str): A unique identifier of an organisation
        request: A pydantic schema that defines the message request parameters
        room_id: A unique identifier of the room where the message is being sent to.
        sender_id: A unique identifier of the user sending the message
        background_tasks: A daemon thread for publishing centrifugo
    Returns:
        HTTP_201_CREATED {new message sent}:
        A dict containing data about the message that was created (response_output).
            {
                "room_id": "61b3fb328f945e698c7eb396",
                "message_id": "61696f43c4133ddga309dcf6",
                "text": "str",
                "files": "HTTP url(s)"
                "sender_id": "619ba4671a5f54782939d385"
            }
    Raises:
        HTTPException [404]: Sender not in room
        HTTPException [404]: Room does not exist
        HTTPException [424]: "message not sent"
    """
    DB = DataStorage(org_id)
    message_obj = Message(
        **request.dict(), org_id=org_id, room_id=room_id, sender_id=sender_id
    )
    response = await DB.write(MESSAGE_COLLECTION, message_obj.dict())

    if response and response.get("status_code") is None:
        message_obj.message_id = response["data"]["object_id"]
        output_data = {
            "room_id": message_obj.room_id,
            "message_id": message_obj.message_id,
            "sender_id": message_obj.sender_id,
            "text": message_obj.text,
            "files": message_obj.files,
        }
        background_tasks.add_task(
            centrifugo_client.publish, room_id, Events.MESSAGE_CREATE, output_data
        )  # publish to centrifugo in the background
        return JSONResponse(
            content=ResponseModel.success(data=output_data, message="new message sent"),
            status_code=status.HTTP_201_CREATED,
        )
    raise HTTPException(
        status_code=status.HTTP_424_FAILED_DEPENDENCY,
        detail={"Message not sent": response},
    )


@router.get(
    "/org/{org_id}/rooms/{room_id}/messages",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"detail": "Messages not found"},
    },
)
async def get_all_messages(org_id: str, room_id: str):
    """Reads all messages in the collection.

    Args:
        org_id (str): A unique identifier of an organisation
        room_id: A unique identifier of the room where the message is being sent to.

    Returns:
        HTTP_200_OK {messages retrieved}:
        A list containing data about all the messages in the collection.
            {
                "status": "success",
                "message": "messages retrieved",
                "data": [
                    {
                    "_id": "61b8ca9878fb01b18fac140f",
                    "created_at": "2021-12-15 20:49:52.445747",
                    "files": [
                        "https://cdn.iconscout.com/icon/free/png-256/"
                    ],
                    "message_id": null,
                    "org_id": "619ba4671a5f54782939d384",
                    "reactions": [],
                    "room_id": "619e28c31a5f54782939d59a",
                    "saved_by": [],
                    "sender_id": "61696f5ac4133ddaa309dcfe",
                    "text": "test after switching back to Any",
                    "threads": []
                    }
                ]

    Raises:
        HTTP_404_NOT_FOUND: "Messages not found"
    """
    DB = DataStorage(org_id)
    messages = await DB.read(MESSAGE_COLLECTION, {"org_id": org_id, "room_id": room_id})

    try:
        if messages:
            return JSONResponse(
                content=ResponseModel.success(
                    data=messages, message="messages retrieved"
                ),
                status_code=status.HTTP_200_OK,
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Messages not found": messages},
        )
    except Exception as e:
        raise e


@router.get(
    "/org/{org_id}/rooms/{room_id}/messages/{message_id}",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"detail": "Message not found"},
    },
)
async def get_message_by_id(org_id: str, room_id: str, message_id: str):
    """Retrieves a message in the collection.

    Args:
        org_id (str): A unique identifier of an organisation
        room_id: A unique identifier of the room where the message is being sent to.
        message_id: A unique identifier of the message to be retrieved

    Returns:
        HTTP_200_OK {message retrieved}:
        A dict containing data about the message in the collection based on the message schema.
            {
                "status": "success",
                "message": "message retrieved",
                "data": {
                    "_id": "61bc6b6078fb01b18fac1427",
                    "created_at": "2021-12-17 10:47:22.673050",
                    "files": [],
                    "message_id": null,
                    "org_id": "619ba4671a5f54782939d384",
                    "reactions": [],
                    "room_id": "619e28c31a5f54782939d59a",
                    "saved_by": [],
                    "sender_id": "619ba4671a5f54782939d385",
                    "text": "yet another check",
                    "threads": []
                    }
                }
                
    Raises:
        HTTP_HTTP_404_NOT_FOUND: Message not found
    """
    DB = DataStorage(org_id)
    message = await DB.read(
        MESSAGE_COLLECTION, {"org_id": org_id, "room_id": room_id, "_id": message_id}
    )
    try:
        if message:
            return JSONResponse(
                content=ResponseModel.success(
                    data=message, message="message retrieved"
                ),
                status_code=status.HTTP_200_OK,
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Message not found": message},
        )
    except Exception as e:
        raise e