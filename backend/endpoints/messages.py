from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Body
from schema.message import Message, MessageRequest, MessageUpdateRequest, Reaction
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.db import DataStorage
from utils.mssg_utils import get_mssg
from typing import Dict

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
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"detail": "Messages not found"},
    },
)
async def get_all_messages(org_id: str, room_id: str): 
    """Reads all messages in the collection.

    Args:
        org_id (str): A unique identifier of an organisation
        request: A pydantic schema that defines the message request parameters
        room_id: A unique identifier of the room where the message is being sent to.

    Returns:
        HTTP_200_OK {messages retrieved}:
        A dict containing data about the messages in the collection based on the message schema (response_output).
            {
                "_id": "61b8caec78fb01b18fac1410",
                "created_at": "2021-12-14 16:40:43.302519",
                "files": [],
                "message_id": null,
                "org_id": "619ba4671a5f54782939d384",
                "reactions": [],
                "room_id": "619e28c31a5f54782939d59a",
                "saved_by": [],
                "sender_id": "61696f5ac4133ddaa309dcfe",
                "text": "testing messages",
                "threads": []
            }

    Raises:
        HTTP_404_NOT_FOUND: "Messages not found"
    """
    DB = DataStorage(org_id)
    if org_id and room_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid parameters",
        )
    try:
        messages = await DB.read(MESSAGE_COLLECTION, {"org_id": org_id, "room_id": room_id})
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
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"detail": "Message not found"},
    },
)
async def get_message_by_id(org_id: str, room_id: str, message_id: str):
    """Retrieves a message in the collection.

    Args:
        org_id (str): A unique identifier of an organisation
        request: A pydantic schema that defines the message request parameters
        room_id: A unique identifier of the room where the message is being sent to.
        message_id: A unique identifier of the message to be retrieved

    Returns:
        HTTP_200_OK {message retrieved}:
        A dict containing data about the message in the collection based on the message schema (response_output).
            {
                "_id": "61b8caec78fb01b18fac1410",
                "created_at": "2021-12-14 16:40:43.302519",
                "files": [],
                "message_id": null,
                "org_id": "619ba4671a5f54782939d384",
                "reactions": [],
                "room_id": "619e28c31a5f54782939d59a",
                "saved_by": [],
                "sender_id": "61696f5ac4133ddaa309dcfe",
                "text": "testing messages",
                "threads": []
            }

    Raises:
        HTTP_HTTP_404_NOT_FOUND: Message not found
    """
    DB = DataStorage(org_id)
    if org_id and room_id and message_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid parameters",
        )
    try:
        message = await get_mssg(org_id=org_id, room_id=room_id, message_id=message_id)
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


@router.put(
    "/org/{org_id}/rooms/{room_id}/messages/{message_id}",
    response_model=ResponseModel,
            responses={
                status.HTTP_200_OK: {"description": "message updated"},
                status.HTTP_404_NOT_FOUND: {"description": "message not found"},
                status.HTTP_403_FORBIDDEN: {"description": "you are not authorized to edit this message"},
                status.HTTP_424_FAILED_DEPENDENCY: {"description": "message not updated"}
            })
async def update_message(
    request: MessageUpdateRequest,
    org_id: str,
    room_id: str,
    sender_id: str,
    message_id: str,
    background_tasks: BackgroundTasks
):
    """
    Update a message

    Args:
        request: Request object
        org_id: A unique identifier of the organization.
        room_id: A unique identifier of the room.
        sender_id: A unique identifier of the sender.
        message_id: A unique identifier of the message that is being updated.

    Returns:
        HTTP_200_OK {message updated successfully}:
        A dict containing data about the message that was updated (response_output).
            {
                "_id": "61b8caec78fb01b18fac1410",
                "created_at": "2021-12-14 16:40:43.302519",
                "files": [],
                "message_id": null,
                "org_id": "619ba4671a5f54782939d384",
                "reactions": [],
                "room_id": "619e28c31a5f54782939d59a",
                "saved_by": [],
                "sender_id": "61696f5ac4133ddaa309dcfe",
                "text": "testing messages",
                "threads": []
            }

    Raises:
        HTTP_404_FAILED_DEPENDENCY: Message not found
        HTTP_424_FAILED_DEPENDENCY: Message not updated
        HTTP_403_FORBIDDEN: You are not authorized to edit this message
    """
    DB = DataStorage(org_id)
    if org_id and room_id and message_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid parameters",
        )
    mssg = await get_mssg(org_id=org_id, room_id=room_id, message_id=message_id)
    if not mssg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    if mssg["sender_id"] != sender_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to edit this message",
        )

    payload = request.dict()
    try:
        message = await DB.update(
            MESSAGE_COLLECTION, document_id=message_id, data=payload
        )
        if message:
            edited_mssg = {
            "text": payload["text"],
        }
            background_tasks.add_task(
                centrifugo_client.publish, room_id, Events.MESSAGE_UPDATE, edited_mssg
            )  # publish to centrifugo in the background
            return JSONResponse(
                content=ResponseModel.success(
                    data=edited_mssg, message="message updated successfully"
                ),
                status_code=status.HTTP_200_OK,
            )
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={"message not updated": message},
        )
    except Exception as e:
        raise e



@router.put(
    "/org/{org_id}/rooms/{room_id}/messages/{message_id}/reactions",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"detail": "message not found"},
        424: {"detail": "failed to add new reaction to message"},
    },
)
async def add_reaction(
    request: Reaction,
    org_id: str,
    room_id: str,
    sender_id: str,
    message_id: str,
    background_tasks: BackgroundTasks,
    new_reaction: Dict[str, Reaction] = Body(...),
):
    """
    Add a reaction to a message
    
    Args:
        request: Request object
        org_id: A unique identifier of the organization.
        room_id: A unique identifier of the room.
        sender_id: A unique identifier of the sender.
        message_id: A unique identifier of the message that is being updated.
        new_reaction: A dict containing data about the reaction that is being added.
            {
                "reaction_id": "61b8caec78fb01b18fac1410",
                "reaction_type": "like",
                "reaction_value": "1"
            }

    Returns:
        HTTP_200_OK {message updated successfully}:
        A dict containing data about the message that was updated (response_output).
            {
                "_id": "61b8caec78fb01b18fac1410",
                "created_at": "2021-12-14 16:40:43.302519",
                "files": [],
                "message_id": null,
                "org_id": "619ba4671a5f54782939d384",
                "reactions": [],
                "room_id": "619e28c31a5f54782939d59a",
                "saved_by": [],
                "sender_id": "61696f5ac4133ddaa309dcfe",
                "text": "testing messages",
                "threads": []
            }

    Raises:
        HTTP_404_NOT_FOUND: Message not found
        HTTP_424_FAILED_DEPENDENCY: Failed to add new reaction to message
    """
    DB = DataStorage(org_id)
    if org_id and room_id and message_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid parameters",
        )
    mssg = await get_mssg(org_id=org_id, room_id=room_id, message_id=message_id)
    if not mssg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    if mssg["sender_id"] != sender_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to edit this message",
        )

    try:
        reaction = await DB.add_reaction(
            MESSAGE_COLLECTION,
            document_id=message_id,
            reaction_id=new_reaction["reaction_id"],
            reaction_type=new_reaction["reaction_type"],
            reaction_value=new_reaction["reaction_value"],
        )
        if reaction:
            background_tasks.add_task(
                centrifugo_client.publish,
                room_id,
                Events.MESSAGE_REACTION_ADD,
                new_reaction,
            )  # publish to centrifugo in the background
            return JSONResponse(
                content=ResponseModel.success(
                    data=reaction, message="reaction added successfully"
                ),
                status_code=status.HTTP_200_OK,
            )
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={"failed to add new reaction to message": reaction},
        )
    except Exception as e:
        raise e
