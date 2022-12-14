from fastapi import (APIRouter, BackgroundTasks, Depends, File, Header,
                     HTTPException, UploadFile, status)
from schema.message import Message, MessageFormData, MessageRequest
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.chat_notification import Notification
from utils.files_utils import upload_files
from utils.message_utils import create_message, get_message, get_room_messages
from utils.message_utils import update_message as edit_message
from utils.paginator import page_urls

router = APIRouter()
notification = Notification()


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
    background_tasks: BackgroundTasks,
    request: MessageRequest = Depends(MessageFormData.as_form),
    attachments: list[UploadFile] = File([]),
    token: str = Header(""),
):
    """
    Uploads files to the file storage service, then
    Creates and sends a message from a user inside a room with the file urls.

    Args:
        org_id (str): The organization id
        room_id (str): The room id
        background_tasks (BackgroundTasks): Background tasks to run
        request (MessageRequest, optional): The message request.
        Defaults to Depends(MessageFormData.as_form).
        attachments (list[UploadFile], optional): The files to upload.
        Defaults to File([]).
        token (str, optional): The user's token. Defaults to Header("").

    Raises:
        HTTPException [401]: If token is not provided if uploading files.
        HTTPException [404]: Room does not exist or
        Sender not a member of this room.
        HTTPException [424]: If the file storage service is not available or
        Message not sent.

    Returns:
        In case of success:
```json
        {
            "status": "success",
            "message": "New message sent",
            "data": {
                "sender_id": "string",
                "emojis": [],
                "richUiData": {
                "blocks": [
                    {
                    "key": "string",
                    "text": "string",
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
                "room_id": "string",
                "org_id": "string",
                "message_id": "string",
                "edited": false,
                "threads": []
            }
        }
```
        In case of failure:
```json
        {
            "status": "error",
            "message": "Error message",
        }
```
    """

    # Validate the sender_id and room_id
    message = Message(
        **request.dict(), org_id=org_id,
        room_id=room_id)

    # Upload file if any
    if attachments:
        file_urls = await upload_files(
            token=token,
            attachments=attachments,
            org_id=org_id,
        )
        message.files = file_urls

    response = await create_message(org_id=org_id, message=message)
    if not response or response.get("status_code"):
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={
                "status": "error",
                "message": "Message not sent"
            },
        )

    message.message_id = response["data"]["object_id"]

    # Publish to centrifugo in the background.
    background_tasks.add_task(
        centrifugo_client.publish,
        room_id,
        Events.MESSAGE_CREATE,
        message.dict(),
    )
    # instantiate the Notication's function that handles message notification
    try:
        await notification.messages_trigger(message_obj=message)
    except Exception as e:
        print("Novu message error", e)

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
    response_model=list[Message],
    status_code=status.HTTP_200_OK,
    responses={424: {"detail": "ZC Core failed"}},
)
async def get_messages(
    org_id: str, room_id: str, page: int = 1, size: int = 15, created_at: int = None
):
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

    response = await get_room_messages(org_id, room_id, page, size, created_at)

    paging, total_count = await page_urls(
        page,
        size,
        org_id,
        room_id,
        endpoint=f"/api/v1/org/{org_id}/rooms/{room_id}/messages",
    )

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Zc Core failed",
        )

    result = {
            "data": response,
            "created_at": created_at,
            "page": page,
            "size": size,
            "total": total_count,
            "previous": paging.get('previous'),
            "next": paging.get('next')
    }

    return JSONResponse(
        content=ResponseModel.success(data=result, message="Messages retrieved"),
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/org/{org_id}/rooms/{room_id}/messages/{message_id}",
    response_model=list[Message],
    status_code=status.HTTP_200_OK,
    responses={424: {"detail": "ZC Core failed"}},
)   

async def get_single_message(org_id: str, room_id: str, message_id: str):
    """Fetches a single message.

    Args:
        org_id (str): A unique identifier of an organization.
        room_id (str): A unique identifier of the room where messages are fetched from.
        message_id (str): The id of the message to be retrieved.

    Returns:
    
        A dict containing a list of message objects.
        {
            "status": "success",
            "message": "Messages retrieved",
            "data": {
                "_id": "61e75bc065934b58b8e5d223",
                "created_at": "2022-02-02 17:57:02.630439",
                "edited": true,
                "emojis": [],
                "files": [],
                "message_id": null,
                "org_id": "637f6f28601ce3fc5dc738f3",
                "richUiData": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "4c3f3",
                        "text": "sdfuigd",
                        "type": "unstyled"
                    }
                ],
                "entityMap": {}
            },
            "room_id": "637f6f2d601ce3fc5dc738f5",
            "saved_by": [],
            "sender_id": "637f6f28601ce3fc5dc738f4",
            "threads": [
                {
                "emojis": [],
                "richUiData": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "f3s6p",
                            "text": "It's just Mykie here again!",
                            "type": "unstyled"
                        }
                    ],
                    "entityMap": {}
                },
                "sender_id": "637f6f28601ce3fc5dc738f4",
                "thread_id": "1504c7aa-77d7-11ed-ae42-ec8eb54be004",
                "timestamp": 1669917458839
            }
        ],
        "timestamp": 1669999250973
    }
}

    Raises:
        HTTPException [424]: Zc Core failed"""

    response = await get_message(org_id, room_id, message_id)

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

    return JSONResponse(
        content=ResponseModel.success(data=response, message="Messages retrieved"),
        status_code=status.HTTP_200_OK,
    )