from datetime import datetime

from bson.objectid import ObjectId
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from schema.response import ResponseModel
from schema.room import Role, RoomType
from utils.db import DB
from utils.room_utils import ROOM_COLLECTION
from utils.sidebar import sidebar

router = APIRouter()


class InstallPayload(BaseModel):
    """Installation payload model."""

    organisation_id: str
    user_id: str


@router.post("/install")
async def dm_install(payload: InstallPayload):
    """This endpoint is called when an organisation wants to install the
    DM plugin for their workspace."""

    channel = {
        "room_name": "general",
        "room_type": RoomType.CHANNEL,
        "room_members": {
            payload.user_id: {"role": Role.ADMIN, "starred": False, "closed": False}
        },
        "created_at": str(datetime.utcnow()),
        "description": "",
        "topic": "",
        "is_private": False,
        "is_archived": False,
        "org_id": payload.organisation_id,
        "created_by": payload.user_id,
    }

    dm = {
        "room_name": payload.user_id,
        "room_type": RoomType.DM,
        "room_members": {
            payload.user_id: {"role": Role.ADMIN, "starred": False, "closed": False}
        },
        "created_at": str(datetime.utcnow()),
        "description": "",
        "topic": "",
        "is_private": False,
        "is_archived": False,
        "org_id": payload.organisation_id,
        "created_by": payload.user_id,
    }

    channel_res = await DB.write(ROOM_COLLECTION, data=channel)

    if channel_res is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="unable to create default Channel",
        )
#    if isinstance(channel_res, dict):
#        raise HTTPException(
#            status_code=status.HTTP_424_FAILED_DEPENDENCY,
#            detail="unable to remove room member",
#        )

    dm_res = await DB.write(ROOM_COLLECTION, data=dm)

    if dm_res is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="unable to create default DM",
        )
#    if isinstance(dm_res, dict) is dict:
#        raise HTTPException(
#            status_code=status.HTTP_424_FAILED_DEPENDENCY,
#            detail="unable to remove room member",
#        )

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
        org_id (str): The organization id
        member_id (str): The member id of user logged in
        room_type (RoomType): The room type

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
   # if room_type is None:
   #     raise HTTPException(
   #         status_code=status.HTTP_400_BAD_REQUEST, detail="room_type is required"
   #     )

    data = await sidebar.format_data(org, user, RoomType.CHANNEL)
    return JSONResponse(
        content=ResponseModel.success(data), status_code=status.HTTP_200_OK
    )
