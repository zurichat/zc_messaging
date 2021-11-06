from fastapi import APIRouter, BackgroundTasks, status
from fastapi.responses import JSONResponse
from schema.room import Room
from utils.centrifugo_handler import Events, centrifugo_client
from utils.db_handler import DB
from utils.utility import get_rooms, sidebar_emitter

router = APIRouter()


async def extra_room_info(room_data: dict):
    """provides some extra room information to be displayed on the sidebar
    Args:
        room_data {dict}: {object of newly created room}
    Returns:
        {dict}

    """

    if room_data["plugin_name"] == "channels":
        return {
            "category": "channel",
            "group_name": "channel",
            "room_name": room_data["room_name"],
        }
    return {"category": "direct messaging", "group_name": "dm", "room_name": None}


@router.post("/org/{org_id}/members/{member_id}/room")
async def create_room(
    org_id: str, member_id: str, request: Room, background_tasks: BackgroundTasks
):
    """Creates a room between users.
    It takes the id of the users involved, sends a write request to the database .
    Then returns the room id when a room is successfully created
    Args:
        org_id (str): id of organisation
        request: room schema
        member_id: id of room_creator
    Returns:
        HTTP_200_OK (room already exist): {room_id}
        HTTP_201_CREATED (new room created): {room_id}
        HTTP_424_FAILED_DEPENDENCY: room creation unsuccessful
        HTTP_406_NOT_ACCEPTABLE: max number of dm users exceeded
    """
    room_data = request.dict()
    room_members = set(room_data["room_members"])
    if len(room_members) > 9:
        return JSONResponse(
            content={"message": "Cannot have more than 9 users in a DM"},
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
        )
    user_rooms = await get_rooms(org_id)  # add member_id after adding it to function
    if isinstance(user_rooms, list):
        for room in user_rooms:
            if room_members == set(room_data["room_members"]):
                return JSONResponse(
                    content={"room_id": room["_id"]}, status_code=status.HTTP_200_OK
                )
    elif user_rooms is None:
        return JSONResponse(
            content="unable to read database", status=status.HTTP_424_FAILED_DEPENDENCY
        )

    elif user_rooms.get("status_code") != 404 or user_rooms.get("status_code") != 200:
        return JSONResponse(
            content="unable to read database",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )

    response = await DB.write("rooms", data=room_data)
    if response and response.get("status") == 200:
        room_id = {"room_id": response.get("data").get("object_id")}
        other_info = await extra_room_info(room_data)
        response_output = await sidebar_emitter(
            org_id,
            member_id,
            category=other_info["category"],
            group_name=other_info["group_name"],
        )  # getting the response data
        background_tasks.add_task(
            centrifugo_client.publish,
            room=f"{org_id}_{member_id}_sidebar",
            event=Events.SIDEBAR_UPDATE,
            data=response_output,
        )  # publish to centrifugo in the background
        return JSONResponse(content=room_id, status_code=status.HTTP_201_CREATED)
    return JSONResponse(
        content=f"unable to create room, Reason: {response}",
        status_code=status.HTTP_424_FAILED_DEPENDENCY,
    )
