from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from schema.response import ResponseModel
from schema.room import Room, RoomRequest
from utils.db import DataStorage
from utils.room_utils import ROOM_COLLECTION
from utils.sidebar import sidebar

router = APIRouter()


@router.post(
    "/org/{org_id}/members/{member_id}/rooms",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        200: {"detail": {"room_id": "room_id"}},
        424: {"detail": "ZC Core Failed"},
    },
)
async def create_room(
    org_id: str, member_id: str, request: RoomRequest, background_tasks: BackgroundTasks
):
    """Creates a room between users.

    Registers a new document to the database collection.
    Returns the document id if the room is successfully created or already exist
    while publishing to the user sidebar in the background

    Args:
        org_id (str): A unique identifier of an organisation
        request: A pydantic schema that defines the room request parameters
        member_id: A unique identifier of the member creating the room

    Returns:
        HTTP_200_OK (room already exist): {room_id}
        HTTP_201_CREATED (new room created): {room_id}
    Raises
        HTTP_424_FAILED_DEPENDENCY: room creation unsuccessful
    """

    DB = DataStorage(org_id)
    room_obj = Room(**request.dict(), org_id=org_id, created_by=member_id)
    response = await DB.write(ROOM_COLLECTION, data=room_obj.dict())
    if response and response.get("status_code", None) is None:
        room_id = {"room_id": response.get("data").get("object_id")}

        background_tasks.add_task(
            sidebar.publish,
            org_id,
            member_id,
            room_obj.room_type,
        )  # publish to centrifugo in the background

        room_obj.id = room_id["room_id"]  # adding the room id to the data
        return JSONResponse(
            content=ResponseModel.success(data=room_obj.dict(), message="room created"),
            status_code=status.HTTP_201_CREATED,
        )

    raise HTTPException(
        status_code=status.HTTP_424_FAILED_DEPENDENCY,
        detail="unable to create room",
    )
