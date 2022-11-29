from fastapi import (APIRouter, BackgroundTasks, Depends, File, HTTPException,
                     UploadFile, status)
from fastapi.security import OAuth2PasswordBearer
from schema.message import Message, MessageRequest
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.file_storage import FileStorage
from utils.message_utils import create_message, get_message, get_room_messages
from utils.message_utils import update_message as edit_message

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post(
    "/org/{org_id}/rooms/{room_id}/messages",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Room or sender not found"},
        424: {"description": "ZC Core failed"},
    },
)
async def send_message(
    org_id: str,
    room_id: str,
    token: str,
    background_tasks: BackgroundTasks,
    request: MessageRequest = Depends(),
    file: UploadFile = File(default=None),  # NOTE Unable to upload multiple files
):

    """Creates and sends a message from a user inside a room.

    Registers a new document to the messages database collection while
    publishing to all members of the room in the background.

    Args:
        org_id (str): A unique identifier of an organisation.
        request (MessageRequest): A pydantic schema that defines the message request parameters.
        room_id (str): A unique identifier of the room where the message is being sent to.
        background_tasks (BackgroundTasks): A background task for publishing to all
                                            members of the room.

    Returns:
        A dict containing data about the message that was created.

        {
            "status": "success",
            "message": "new message sent",
            "data": {
                "sender_id": "619bab3b1a5f54782939d400",
                "emojis": [],
                "richUiData": {
                "blocks": [
                    {
                    "key": "eljik",
                    "text": "Larry Gaaga",
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
                "timestamp": 0,
                "created_at": "2022-02-01 19:20:55.891264",
                "room_id": "61e6855e65934b58b8e5d1df",
                "org_id": "619ba4671a5f54782939d384",
                "message_id": "61f98d0665934b58b8e5d286",
                "edited": false,
                "threads": []
            }
        }

    Raises:
        HTTPException [404]: Room does not exist || Sender not a member of this room.
        HTTPException [424]: Message not sent.
    """
    new_obj = {**request.dict()}
    file_urls = []

    if file is not None:
        file_obj = [('file', (f'{file.filename}', f'{file.file}', f'{file.content_type}'))]

        fileStorage = FileStorage(org_id)
        file_url = await fileStorage.files_upload(file_obj, token)
        if file_url:
            file_urls.append(file_url)

    new_obj['files'] = file_urls
    message = Message(**new_obj, org_id=org_id, room_id=room_id)

    response = await create_message(org_id=org_id, message=message)

    if not response or response.get("status_code"):
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={"Message not sent": response},
        )
    message.message_id = response["data"]["object_id"]

    # Publish to centrifugo in the background.
    background_tasks.add_task(
        centrifugo_client.publish,
        room_id,
        Events.MESSAGE_CREATE,
        message.dict(),
    )
    return JSONResponse(
        content=ResponseModel.success(data=message.dict(), message="new message sent"),
        status_code=status.HTTP_201_CREATED,
    )


@router.put(
    "/org/{org_id}/rooms/{room_id}/messages/{message_id}",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "You are not authorized to edit this message"},
        404: {"description": "Message not found"},
        424: {"description": "Message not edited"},
    },
)
async def update_message(
    org_id: str,
    room_id: str,
    message_id: str,
    request: MessageRequest,
    background_tasks: BackgroundTasks,
):
    """Updates a message sent in a room.

    Edits an existing message document in the messages database collection while
    publishing to all members of the room in the background.

    Args:
        org_id: A unique identifier of the organization.
        room_id: A unique identifier of the room.
        message_id: A unique identifier of the message that is being edited.
        request: A pydantic schema that defines the message request parameters.
        background_tasks: A background task for publishing to all
                          members of the room.

    Returns:
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
        HTTPException [401]: You are not authorized to edit this message.
        HTTPException [404]: Message not found.
        HTTPException [424]: Message not edited.
    """
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

    edited_message = await edit_message(org_id, message_id, payload)

    if not edited_message or edited_message.get("status_code"):
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={"message not edited": edited_message},
        )

    payload["edited"] = True
    message.update(payload)

    # Publish to centrifugo in the background.
    background_tasks.add_task(
        centrifugo_client.publish, room_id, Events.MESSAGE_UPDATE, message
    )

    return JSONResponse(
        content=ResponseModel.success(data=message, message="Message edited"),
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/org/{org_id}/rooms/{room_id}/messages",
    response_model=[].append(Message),
    status_code=status.HTTP_200_OK,
    responses={424: {"detail": "ZC Core failed"}},
)
async def get_messages(org_id: str, room_id: str, page: int = 1, limit: int = 15):
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
                ...
            ]
        }

    Raises:
        HTTPException [424]: Zc Core failed
    """

    response = await get_room_messages(org_id, room_id, page, limit)
    if response == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room does not exist or no message found",
        )

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Zc Core failed",
        )

    result = {
            "data": response,
            "page": page,
            "size": limit
    }

    return JSONResponse(
        content=ResponseModel.success(data=result, message="Messages retrieved"),
        status_code=status.HTTP_200_OK,
    )
