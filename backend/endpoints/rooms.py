from backend.schema.room import Role, RoomMember
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from schema.response import ResponseModel
from schema.room import Room, RoomRequest
from utils.db import DB
from utils.room_utils import ROOM_COLLECTION
from utils.sidebar import sidebar
from utils.room_utils import get_room

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

@router.delete("/org/{org_id}/members/{member_id}/rooms/{room_id}",
    response_model=ResponseModel, )
async def remove_member(org_id: str, member_id: str, room_id: str, mem_id: str):
    """Removes a member from a room.

    Fetches the room which the member is removed from from the database collection
    Pops the member being removed from the room's members dict
    Updates the database collection with the new room
    *Returns the room dict if member was removed successfully
    *while publishing to the user sidebar in the background

    Args:
        org_id (str): A unique identifier of an organisation
        request: A pydantic schema that defines the room request parameters
        member_id (str): A unique identifier of the member removing another member
        room_id (str): A unique identifier of the room a member is being removed from
        memb_id (str): A unique identifier of the member being removed from the room

    Returns:
        HTTP_200_OK (member removed from room): {room}
    Raises
        HTTP_404_NOT_FOUND: room or member not found
        HTTP_424_FAILED_DEPENDENCY: member removal unsuccessful
    """

    room_obj = await get_room(org_id, room_id)

    if not room_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="room does not exist",
        )
    
    if member_id not in room_obj["room_members"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not a member of the room",
        )
    
    if member_id == mem_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="unable to remove room member",
        )

    member: RoomMember = room_obj["room_members"].get(member_id)
    
    if member.role == Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="unable to remove room member",
        )


    remove_member = room_obj["room_members"].pop(mem_id, "not_found")
    
    if remove_member != "not_found":
        update_room = DB.update(ROOM_COLLECTION, room_obj["id"], room_obj)
        if update_room == None:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail="unable to remove room member",
            )
        elif type(update_room) is dict:
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail="unable to remove room member",
            )
        else:
            return JSONResponse(
            content=ResponseModel.success(data=room_obj.dict(), message="member removed successfully from room"),
            status_code=status.HTTP_200_OK,
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="user not a member of the room",
    )