from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from schema.room import Room, RoomResponse
from utils.centrifugo_handler import Events, centrifugo_client
from utils.db_handler import DB
from utils.utility import get_rooms, sidebar_emitter

router = APIRouter()


async def extra_room_info(room_data: dict):
    """provides some extra room information to be displayed on the sidebar

    Args:
        room_data {dict}: {object of newly created room}

    Returns:
        A dict mapping keys to their corresponding value
            {"category": "str", "group_name": str}

    """

    if room_data["plugin_name"] == "channel":
        return {
            "category": "channel",
            "group_name": "channel",
            "room_name": room_data["room_name"],
        }
    return {"category": "direct messaging", "group_name": "dm"}


@router.post(
    "/org/{org_id}/members/{member_id}/room",
    status_code=201,
    response_model=RoomResponse,
    responses={200: {"model": RoomResponse}},
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
        A dict mapping the key room_id to the unique identifier (id) value of the room
            {"room_id: "_id"}

    Raises:
        HTTP_424_FAILED_DEPENDENCY: "room creation unsuccessful" or
            "unable to read database"
        HTTP_406_NOT_ACCEPTABLE: raised when the maximium number of allowed users is exceeded
    """
    room_data = request.dict()
    room_members = set(room_data["room_members"])
    if len(room_members) > 9:
        raise HTTPException(
            status_code=424, detail="Cannot have more than 9 users in a DM"
        )
    query = {}  # yet to figure out the exact query format
    user_rooms = await get_rooms(
        org_id, query
    )  # add member_id after adding it to function
    if isinstance(user_rooms, list):
        for room in user_rooms:
            if room_members == set(room_data["room_members"]):
                return JSONResponse(
                    content={"room_id": room["_id"]}, status_code=status.HTTP_200_OK
                )
    elif user_rooms is None or user_rooms.get("status_code") != 404:
        raise HTTPException(status_code=424, detail="unable to read database")

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
    raise HTTPException(status_code=424, detail="unable to create room")
