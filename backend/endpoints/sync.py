from datetime import datetime

from bson.objectid import ObjectId
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from schema.response import ResponseModel
from schema.room import Role, RoomType
from utils.db import DataStorage
from utils.sidebar import sidebar
from config.settings import settings

router = APIRouter()


@router.post(
    "/install",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"detail": "installtion successful"},
        400: {"detail": "Object id is not valid"},
        422: {"detail": "Field required"},
        424: {"detail": "Instaalltion Failed"},
    },
)
async def dm_install(organisation_id: str = Body(...), user_id: str = Body(...)):
    """This endpoint is called when an organisation wants to install the
    DM plugin for their workspace.

    Args: [dict]: key value pairs of organisation_id and user_id
          sample_payload = {
                "organisation_id": "5e8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f",
                "user_id": "5e8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f"
                }

    Returns: [str]: string response of "installation successful"

    Raises: [HTTPException]: raises an HTTPException if the installation fails
            400: [dict]: if organisation_id or user_id is an invalid object id
            422: [dict]: if the organisation_id or user_id is not found in request body
            424: [dict]: if core service is not available or fails to install
    """
    if not ObjectId.is_valid(organisation_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="organisation id is not a valid object id",
        )
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user id is not a valid object id",
        )

    DB = DataStorage(organisation_id)
    channel = {
        "room_name": "general",
        "room_type": RoomType.CHANNEL,
        "room_members": {
            user_id: {"role": Role.ADMIN, "starred": False, "closed": False}
        },
        "created_at": str(datetime.utcnow()),
        "description": "",
        "topic": "",
        "is_private": False,
        "is_archived": False,
        "org_id": organisation_id,
        "created_by": user_id,
    }

    dm = {
        "room_name": user_id,
        "room_type": RoomType.DM,
        "room_members": {
            user_id: {"role": Role.ADMIN, "starred": False, "closed": False}
        },
        "created_at": str(datetime.utcnow()),
        "description": "",
        "topic": "",
        "is_private": True,
        "is_archived": False,
        "org_id": organisation_id,
        "created_by": user_id,
    }

    channel_res = await DB.write(settings.ROOM_COLLECTION, data=channel)

    if channel_res is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Unable to create default channel",
        )

    dm_res = await DB.write(settings.ROOM_COLLECTION, data=dm)

    if dm_res is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Unable to create default DM",
        )

    return JSONResponse(
        content="installation successful", status_code=status.HTTP_200_OK
    )


@router.get(
    "/sidebar",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"detail": "Object id is not valid"},
    },
)
async def get_sidebar(org: str, user: str):
    """Provides a response of side bar data for the given room type

    Args:
        org (str): The organization id
        user (str): The member id of user logged in

    Returns:
        [dict]: dict containing sidebar data with status code 200

    Raises:
        HTTPException [dict]: dict containing error message and 400 status code
    """
    if not ObjectId.is_valid(org):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="org is not a valid object id",
        )
    if not ObjectId.is_valid(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user is not a valid object id",
        )

    channel_data = await sidebar.format_data(org, user, RoomType.CHANNEL)
    dm_data = await sidebar.format_data(org, user, RoomType.DM)
    return JSONResponse(
        content=ResponseModel.success([channel_data, dm_data]),
        status_code=status.HTTP_200_OK,
    )
