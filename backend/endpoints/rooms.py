from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from schema.response import ResponseModel
from schema.room import Room
from utils.centrifugo import Events, centrifugo_client
from utils.db import DB
from utils.room_utils import get_org_rooms, sidebar

router = APIRouter()


@router.post(
    "/org/{org_id}/members/{member_id}rooms",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
)
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
    """
    room_data = request.dict()
    plugin_name = room_data.get("plugin_name")
    room_name = room_data.get("room_name")
    room_member_ids = list(room_data.get("room_member_ids").keys())
    rooms = await get_org_rooms(org_id=org_id, category=plugin_name)
    print("rooms", rooms)

    if rooms:
        if plugin_name == "channel" and room_name.casefold() in [
            room["room_name"].casefold() for room in rooms
        ]:
            return JSONResponse(
                ResponseModel.fail("room already exist", data={"room_name": room_name}),
                status_code=status.HTTP_200_OK,
            )

        if plugin_name == "dm":
            for room in rooms:
                if set(room["room_members"].keys()) == set(room_member_ids):

                    return JSONResponse(
                        content=ResponseModel.fail(
                            "room already exist", data={"room_id": room["room_id"]}
                        ),
                        status_code=status.HTTP_200_OK,
                    )

        response = await DB.write("dm_rooms", data=room_data)
        if response and response.get("status") == 200:
            room_id = {"room_id": response.get("data").get("object_id")}
            centrifugo_data = await sidebar.format(
                org_id,
                member_id,
                plugin=plugin_name,
            )  # getting the response data

            background_tasks.add_task(
                centrifugo_client.publish,
                room=f"{org_id}_{member_id}_sidebar",
                event=Events.SIDEBAR_UPDATE,
                data=centrifugo_data,
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
