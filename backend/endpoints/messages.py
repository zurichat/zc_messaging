from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from schema.message import Message, MessageRequest, MessageUpdate
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.db import DataStorage
from utils.message_utils import MESSAGE_COLLECTION, get_message

router = APIRouter()


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


@router.put(
    "/org/{org_id}/rooms/{room_id}/messages/{message_id}",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "you are not authorized to edit this message"},
        404: {"description": "message not found"},
        424: {"description": "message not edited"},
    },
)
async def update_message(
    request: MessageUpdate,
    org_id: str,
    room_id: str,
    message_id: str,
    background_tasks: BackgroundTasks,
):
    """
    Update a message

    Args:
        request: Request object
        org_id: A unique identifier of the organization.
        room_id: A unique identifier of the room.
        message_id: A unique identifier of the message that is being edited.
        background_tasks: A daemon thread for publishing to centrifugo

    Returns:
        HTTP_200_OK {Message edited}:
        A dict containing data about the message that was edited.
            {
                "room_id": "619e28c31a5f54782939d59a",
                "message_id": "61ba9b0378fb01b18fac1420",
                "sender_id": "619ba4671a5f54782939d385",
                "text": "xxxxxxxxxxxxxxxxx"
            }

    Raises:
        HTTPException [401]: You are not authorized to edit this message
        HTTPException [404]: Message not found
        HTTPException [424]: Message not edited
    """
    DB = DataStorage(org_id)
    message = await get_message(org_id, room_id, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    payload = request.dict()
    if message["sender_id"] != payload["sender_id"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to edit this message",
        )
        
    edited_message = await DB.update(
        MESSAGE_COLLECTION, document_id=message_id, data=payload
    )
    if edited_message:
        new_data = {
            "room_id": room_id,
            "message_id": message_id,
            "sender_id": payload["sender_id"],
            "text": payload["text"],
            "edited": True,
        }
        
        background_tasks.add_task(
            centrifugo_client.publish, room_id, Events.MESSAGE_UPDATE, new_data
        )  # publish to centrifugo in the background
        return JSONResponse(
            content=ResponseModel.success(data=new_data, message="Message edited"),
            status_code=status.HTTP_200_OK,
        )
    raise HTTPException(
        status_code=status.HTTP_424_FAILED_DEPENDENCY,
        detail={"message not edited": edited_message},
    )
