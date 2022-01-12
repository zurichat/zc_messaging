from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi_pagination import Page, add_pagination, paginate
from schema.message import Message, MessageRequest
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.db import DataStorage
from utils.message_utils import (MESSAGE_COLLECTION, get_message,
                                 get_room_messages)

router = APIRouter()


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
    org_id,
    room_id,
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
                "sender_id": "619ba4671a5f54782939d385",
                "emojis": [],
                "richUiData": {
                "blocks": [
                    {
                    "key": "eljik",
                    "text": "HI, I'm mark.. new here",
                    "type": "unstyled",
                    "depth": 0,
                    "inlineStyleRanges": [],
                    "entityRanges": [],
                    "data": {}
                    }
                ],
                "entityMap": {}
                },
                "files": [],
                "saved_by": [],
                "created_at": "2021-12-22 22:38:33.075643",
                "room_id": "619e28c31a5f54782939d59a",
                "org_id": "619ba4671a5f54782939d384",
                "message_id": "61c3aa9478fb01b18fac1465",
                "edited": false,
                "threads": []
            }

    Raises:
        HTTPException [404]: Sender not in room
        HTTPException [404]: Room does not exist
        HTTPException [424]: "message not sent"
    """
    DB = DataStorage(org_id)

    message_obj = Message(**request.dict(), org_id=org_id, room_id=room_id)

    response = await DB.write(
        MESSAGE_COLLECTION, message_obj.dict(exclude={"message_id"})
    )

    if response and response.get("status_code") is None:
        message_obj.message_id = response["data"]["object_id"]
        # Publish to centrifugo in the background.
        background_tasks.add_task(
            centrifugo_client.publish,
            room_id,
            Events.MESSAGE_CREATE,
            message_obj.dict(),
        )
        return JSONResponse(
            content=ResponseModel.success(
                data=message_obj.dict(), message="new message sent"
            ),
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
    request: MessageRequest,
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
                "threads": []
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

    payload = request.dict(exclude_unset=True)
    if message["sender_id"] != payload["sender_id"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to edit this message",
        )

    message.update(payload)
    message["edited"] = True
    edited_message = await DB.update(
        MESSAGE_COLLECTION, document_id=message_id, data=message
    )

    if edited_message and edited_message.get("status_code") is None:
        # Publish to centrifugo in the background.
        background_tasks.add_task(
            centrifugo_client.publish, room_id, Events.MESSAGE_UPDATE, message
        )
        return JSONResponse(
            content=ResponseModel.success(data=message, message="Message edited"),
            status_code=status.HTTP_200_OK,
        )
    raise HTTPException(
        status_code=status.HTTP_424_FAILED_DEPENDENCY,
        detail={"message not edited": edited_message},
    )


@router.get(
    "/org/{org_id}/rooms/{room_id}/messages",
    response_model=Page[Message],
    status_code=status.HTTP_200_OK,
    responses={424: {"detail": "ZC Core failed"}},
)
async def get_messages(org_id, room_id):
    """Fetches all messages sent in a particular room.

    Args:
        org_id (str): A unique identifier of an organization
        room_id (str): A unique identifier of the room where messages are fetched from

    Returns:
        A list of message objects

    Raises:
        HTTPException [424]: Zc Core failed
    """
    response = await get_room_messages(org_id, room_id)
    if response is None or "status_code" in response:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Zc Core failed",
        )
    return paginate(response)


add_pagination(router)
