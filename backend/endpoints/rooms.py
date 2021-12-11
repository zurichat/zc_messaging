from backend.schema.room import Role, RoomMember
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from schema.response import ResponseModel
from schema.room import Role, Room, RoomMember, RoomRequest, RoomType
from utils.centrifugo import Events, centrifugo_client
from utils.db import DataStorage
from utils.room_utils import ROOM_COLLECTION, get_room
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

    DB = DataStorage(org_id)
    room_obj = Room(**request.dict(), org_id=org_id, created_by=member_id)

    # check if creator is in room members
    if member_id not in room_obj.room_members.keys():
        room_obj.room_members[member_id] = {
            "role": Role.ADMIN,
            "starred": False,
            "closed": False,
        }

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

<<<<<<< HEAD

@router.put(
    "/org/{org_id}/rooms/{room_id}/members/{member_id}",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"detail": "the max number for a Group_DM is 9"},
        401: {"detail": "member not an admin"},
        403: {"detail": "DM room or not found"},
        424: {"detail": "failed to add new members to room"},
    },
)
async def join_room(
    org_id: str,
    room_id: str,
    member_id: str,
    background_tasks: BackgroundTasks,
    new_members: Dict[str, RoomMember] = Body(...),
):
    """Adds a new member(s) to a room
    Args:
        data: a pydantic schema that defines the request params
        org_id (str): A unique identifier of an organisation
        room_id: A unique identifier of the room to be updated
        member_id: A unique identifier of the member initiating the request
        background_tasks: A parameter that allows tasks to be performed outside of the main function
        new_members: A dictionary of new members to be added to the room

    Returns:
        HTTP_200_OK: {
                        "status": 200,
                        "message": "success",
                        "data": {
                            "matched_documents": 1,
                            "modified_documents": 1
                        }
                    }
    Raises:
        HTTP_400_BAD_REQUEST: the max number for a Group_DM is 9
        HTTP_401_UNAUTHORIZED: member not in room or not an admin
        HTTP_403_FORBIDDEN: DM room or not found
        HTTP_424_FAILED_DEPENDENCY: failed to add new members to room
    """
    DB = DataStorage(org_id)  # initializes the datastorage class with the org id

    members = {
        k: v.dict() for k, v in new_members.items()
    }  # converts RoomMember to dict

    room = await get_room(org_id=org_id, room_id=room_id)

    if not room or room["room_type"] == RoomType.DM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DM room cannot be joined or not found",
        )

    member = room.get("room_members").get(str(member_id))
    if member is None or member["role"] != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="member not in room or not an admin",
        )

    if room["room_type"] == RoomType.CHANNEL:
        room["room_members"].update(members)

    if room["room_type"] == RoomType.GROUP_DM:
        room["room_members"].update(members)
        if len(room["room_members"].keys()) > 9:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="the max number for a Group_DM is 9",
            )

    update_members = {"room_members": room["room_members"]}
    update_response = await DB.update(
        ROOM_COLLECTION, document_id=room_id, data=update_members
    )  # updates the room data in the db collection

    background_tasks.add_task(
        centrifugo_client.publish,
        room=room_id,
        event=Events.ROOM_MEMBER_ADD,
        data=members,
    )  # publish to centrifugo in the background

    if update_response and update_response.get("status_code", None) is None:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=update_members,
        )
    raise HTTPException(
        status_code=status.HTTP_424_FAILED_DEPENDENCY,
        detail="failed to add new members to room",
    )
=======
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
>>>>>>> added remove member from room
