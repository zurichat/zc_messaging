from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from schema.response import ResponseModel
from schema.room import AddToRoom, Role, Room, RoomRequest, RoomType
from utils.centrifugo import Events, centrifugo_client
from utils.db import DataStorage
from utils.room_utils import ROOM_COLLECTION, get_room
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
async def add_to_room(
    org_id: str,
    room_id: str,
    member_id: str,
    data: AddToRoom,
    background_tasks: BackgroundTasks,
):
    """Adds a new member(s) to a room
    Args:
        data: a pydantic schema that defines the request params
        org_id (str): A unique identifier of an organisation
        room_id: A unique identifier of the room to be updated
        member_id: A unique identifier of the member initiating the request
        background_tasks: A parameter that allows tasks to be performed outside of the main function

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
    new_member = data.dict().get("new_member")
    room = await get_room(org_id=org_id, room_id=room_id)

    if not room or room["room_type"] == RoomType.DM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DM room or not found",
        )

    member = room.get("room_members").get(str(member_id))
    if member is None or member["role"] != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="member not in room or not an admin",
        )

    if room["room_type"] == RoomType.CHANNEL:
        room["room_members"].update(new_member)

    if room["room_type"] == RoomType.GROUP_DM:
        room["room_members"].update(new_member)
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
        data=new_member,
    )  # publish to centrifugo in the background

    if update_response and update_response.get("status_code", None) is None:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=update_response,
        )
    raise HTTPException(
        status_code=status.HTTP_424_FAILED_DEPENDENCY,
        detail="failed to add new members to room",
    )
