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
