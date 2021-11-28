from bson.objectid import ObjectId
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from schema.response import ResponseModel
from schema.room import RoomType
from utils.sidebar import sidebar
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse
from backend.schema.custom import ObjId
from backend.schema.response import ResponseModel
from backend.schema.room import Role, RoomMember
from backend.utils.db import DB
from backend.utils.room_utils import ROOM_COLLECTION

from schema.room import Room, RoomRequest, RoomType

router = APIRouter()

class InstallPayload(BaseModel):
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
            payload.user_id: {
                "role": Role.ADMIN,
                "starred": False,
                "closed": False
            }
        }, 
        "created_at": str(datetime.utcnow()),
        "description": "",
        "topic": "",
        "is_private": False,
        "is_archived": False,
        "org_id": payload.organisation_id,
        "created_by": payload.user_id
    }

    dm = {
        "room_name": payload.user_id,
        "room_type": RoomType.DM,
        "room_members": {
            payload.user_id: {
                "role": Role.ADMIN,
                "starred": False,
                "closed": False
            }
        }, 
        "created_at": str(datetime.utcnow()),
        "description": "",
        "topic": "",
        "is_private": False,
        "is_archived": False,
        "org_id": payload.organisation_id,
        "created_by": payload.user_id
    }

    channel_res = await DB.write(ROOM_COLLECTION, data=channel)
    
    if channel_res == None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="unable to remove room member",
        )      
    elif type(channel_res) is dict:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="unable to remove room member",
        )

    dm_res = await DB.write(ROOM_COLLECTION, data=dm)

    if dm_res == None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="unable to remove room member",
        )      
    elif type(dm_res) is dict:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="unable to remove room member",
        )

    return JSONResponse(
        data=None,
        message="installation successful",
        status_code=status.HTTP_200_OK
    )


@router.get(
    "/sidebar",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"detail": "Object id is not valid"},
    },
)
async def get_sidebar(org_id: str, member_id: str, room_type: RoomType):
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
    if not ObjectId.is_valid(org_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="org_id is not a valid object id",
        )
    if not ObjectId.is_valid(member_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="member_id is not a valid object id",
        )
    if room_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="room_type is required"
        )

    data = await sidebar.format_data(org_id, member_id, room_type)
    return JSONResponse(
        content=ResponseModel.success(data), status_code=status.HTTP_200_OK
    )
