from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from schema.response import ResponseModel
from schema.room import AddToRoom, Plugin, Room
from utils.centrifugo import Events, centrifugo_client
from utils.db import DB
from utils.room_utils import get_org_rooms, get_room, sidebar

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
    org_id: str, member_id: str, request: Room, background_tasks: BackgroundTasks
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
    room_data = request.dict()
    plugin_name = room_data.get("plugin_name")
    room_name = room_data.get("room_name")
    room_member_ids = list(room_data.get("room_members").keys())
    rooms = await get_org_rooms(org_id=org_id, plugin=plugin_name)

    if rooms is not None:
        if plugin_name == Plugin.CHANNEL and room_name.casefold() in [
            room["room_name"].casefold() for room in rooms
        ]:
            raise HTTPException(
                status_code=status.HTTP_200_OK, detail={"room_name": room_name}
            )

        if plugin_name == Plugin.DM:
            for room in rooms:
                if set(room["room_members"].keys()) == set(room_member_ids):
                    raise HTTPException(
                        status_code=status.HTTP_200_OK,
                        detail={"room_id": room["_id"]},
                    )

        response = await DB.write("rooms", data=room_data)
        if response and response.get("status_code", None) is None:
            room_id = {"room_id": response.get("data").get("object_id")}
            sidebar_data = await sidebar.format_data(
                org_id,
                member_id,
                plugin=plugin_name,
            )  # getting the response data

            background_tasks.add_task(
                centrifugo_client.publish,
                room=f"{org_id}_{member_id}_sidebar",
                event=Events.SIDEBAR_UPDATE,
                data=sidebar_data,
            )  # publish to centrifugo in the background
            room_data.update(room_id)  # adding the room id to the data

            return JSONResponse(
                content=ResponseModel.success(data=room_data, message="room created"),
                status_code=status.HTTP_201_CREATED,
            )

        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="unable to create room",
        )

    raise HTTPException(
        status_code=status.HTTP_424_FAILED_DEPENDENCY, detail="unable to read database"
    )


@router.put(
    "/org/{org_id}/rooms/{room_id}/",
    status_code=status.HTTP_200_OK,
    responses={
        204: {"detail": "room not found"},
        400: {"detail": "cannot add members to a DM"},
    },
)
async def add_member_to_room(data: AddToRoom, org_id: str, room_id: str):
    """Adds a new member(s) to a room
    Args:
        data: a pydantic schema that defines the request params
        org_id (str): A unique identifier of an organisation
        room_id: A unique identifier of the room to be updated

    Returns:
        HTTP_200_OK: member added
    Raises:
        HTTP_204_NO_CONTENT: room not found
        HTTP_400_BAD_REQUEST: cannot add members to a DM
    """

    new_member = data.dict().get("new_member")
    room = await get_room(org_id=org_id, room_id=room_id)
    data = {}
    if room:
        room_members = room["room_members"]
        if room["plugin_name"] == Plugin.CHANNEL:
            for member in list(new_member.keys()):
                if member not in list(room_members.keys()):
                    datum = {member: new_member.get(str(member))}
                    data.update(datum)
            room_members.update(data)
            return room
        if room["plugin_name"] == Plugin.Group:
            return room
        if room["plugin_name"] == Plugin.DM:
            raise HTTPException(status_code=400, detail="cannot add members to a DM")
        # response = await DB.update("rooms", document_id=room_id, data=room)
    raise HTTPException(status_code=204, detail="room not found")
