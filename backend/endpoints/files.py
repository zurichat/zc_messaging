import inspect
from typing import Any, Type

from fastapi import (APIRouter, BackgroundTasks, Depends, File, Form, Header,
                     HTTPException, UploadFile, status)
from pydantic import AnyHttpUrl, BaseModel, Json
from schema.message import Emoji, Message, MessageRequest
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.file_storage import FileStorage
from utils.message_utils import create_message

router = APIRouter()


# NOTE: The reason for this is because fastapi does not support
# multipart/form-data requests with pydantic models
# https://github.com/tiangolo/fastapi/issues/2387
# used: https://github.com/tiangolo/fastapi/issues/2387#issuecomment-731662551
def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models.
    The as_form class method can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls


@as_form
class MessageFormData(MessageRequest):
    richUiData: Json[Any] = "{}"
    emojis: Json[list[Emoji]] = "[]"
    files: Json[list[AnyHttpUrl]] = "[]"
    saved_by: Json[list[str]] = "[]"


@router.post(
    "/org/{org_id}/room/{room_id}/files/upload",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Room or sender not found"},
        424: {"description": "ZC Core failed"},
    },
)
async def upload_files(
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

        # Token is required for file storage service
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Token is required for file storage service"
                },
            )

        file_store = FileStorage(organization_id=org_id)
        files = [
            file.file for file in attachments
        ]
        response = await file_store.files_upload(files, token)

        if response is None:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail={
                    "status": "error",
                    "message": "File storage service is not available"
                },
            )

        if isinstance(response, str):
            # Meaning there was an error uploading the file
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail={
                    "status": "error",
                    "message": response
                },
            )

        # Extract the urls from the response
        file_urls = [obj["file_url"] for obj in response]

        # NOTE: Currently, the file storage service returns a list of urls
        # that also contains the urls of the files that were previously
        # uploaded. So we need to remove those urls from the list
        file_urls = file_urls[len(file_urls) - len(attachments):]

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

    return JSONResponse(
        content=ResponseModel.success(
            data=message.dict(), message="New message sent"),
        status_code=status.HTTP_201_CREATED,
    )


# from fastapi import HTTPException, status
# from fastapi import APIRouter
# from utils.message_utils import get_room_messages
# from utils.files_utils import zipfiles

# router = APIRouter()


# @router.get("/org/{org_id}/rooms/{room_id}/files")
# async def get_files(org_id: str, room_id: str, page: int = 1,limit:int=15):
#     """
#     An endpoint that returns a list of images files uplaoded to th given room

#     params:
#             org_id: organization id number: "6373eb474746182adae97314",
#             room_id: room id number: "6373eb4f4746182adae97316"
#     return:
#             A list of filepaths urls
#     """

#     room_messages = await get_room_messages(org_id, room_id, page, limit)

#     if not room_messages:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail={"No file was uploaded": room_messages},
#         )

#     file_paths = []

#     for message in room_messages:
#         if len(message["files"]):
#             file_paths = file_paths + message["files"]

#     return zipfiles(file_paths)
