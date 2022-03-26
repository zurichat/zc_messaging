from typing import Any
from utils.db import DataStorage
from config.settings import settings
from schema.room import Room

async def add_room(org_id: str, room: Room) -> dict[str, Any]:
    """Creates a room document in the database.

    Args:
        org_id (str): The organization id where the room is created.
        room (Room): The room object to be saved.

    Returns:
        dict[str, Any]: The response returned by DataStorage's write method.
    """

    db = DataStorage(org_id)

    return await db.write(settings.ROOM_COLLECTION, room.dict())


async def update_room(
    org_id: str, room_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    """Updates a room document in the database.

    Args:
        org_id (str): The organization id where the room is being updated.
        room_id (str): The id of the room to be edited.
        room (dict[str, Any]): The new data.

    Returns:
        dict[str, Any]: The response returned by DataStorage's update method.
    """

    db = DataStorage(org_id)

    return await db.update(settings.ROOM_COLLECTION, room_id, data)
