from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import AnyHttpUrl
from schema.message import Message
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from utils.file_storage import FileStorage

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post(
    "/org/{org_id}/room/{room_id}/sender/{sender_id}/files/upload",
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
    sender_id: str,
    files: list[UploadFile] = File(...),
    token: str = Depends(oauth2_scheme)
):
    """Uploads files to the file storage service

    Args:
        org_id (str): A unique identifier of an organisation.
        room_id (str): A unique identifier of the room where the message
        sender_id (str): A unique identifier of the sender.
        files (list[UploadFile], optional): A list of files to be uploaded.
        Defaults to File(...).
        token (str, optional): A token for authentication.
        Defaults to Depends(oauth2_scheme).

    Raises:
        HTTPException: If the file storage service is not available.

    Returns:
        A dict containing data about the message that was created.
    """    
    # Validate the sender_id and room_id
    message = Message(
        org_id=org_id, room_id=room_id,
        sender_id=sender_id, timestamp=datetime.now().timestamp())

    # upload file
    file_store = FileStorage(organization_id=org_id)
    files = [
        file.file for file in files
    ]
    response = await file_store.files_upload(files, token)

    # Anything other than a list is an error
    if not isinstance(response, list):
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={"Message not sent": response},
        )

    # extract the urls from the response
    file_urls: list[AnyHttpUrl] = [obj["file_url"] for obj in response]
    message.files = file_urls

    return JSONResponse(
        content=ResponseModel.success(
            data=message.dict(), message="Files uploaded successfully"),
        status_code=status.HTTP_201_CREATED,
    )
