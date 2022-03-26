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
