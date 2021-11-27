from bson.objectid import ObjectId
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from schema.response import ResponseModel
from schema.room import RoomType
from utils.sidebar import sidebar

router = APIRouter()


@router.get("/sidebar")
async def get_sidebar(org_id: str, member_id: str, room_type: RoomType):
    """Provides a response of side bar data for the given room type

    Args:
        org_id (str): The organization id
        member_id (str): The member id of user logged in
        room_type (RoomType): The room type

    Raises:
        HTTPException [dict]: dict containing error message and 400 status code

    Returns:
        [dict]: dict containing sidebar data with status code 200
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
