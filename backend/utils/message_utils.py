from typing import Any, Optional

from config.settings import settings
from utils.db import DataStorage


async def get_org_messages(org_id: str) -> Optional[list[dict[str, Any]]]:
    """Gets all messages sent in  an organization.

    Args:
        org_id (str): The organization id

    Returns:
        list[dict]: A list of key value pairs of messages info mapped according to message schema.

        {
            "status": 200,
            "message": "success",
            "data": [
                {
                    "_id": "61e6878165934b58b8e5d1e0",
                    "created_at": "2022-01-18 09:05:32.479911",
                    "edited": false,
                    ...
                },
                {
                    "_id": "61e6878165934b58b8e5d1e1",
                    "created_at": "2022-01-18 09:05:32.479911",
                    "edited": true,
                    ...
                },
                ...
        }
    """

    DB = DataStorage(org_id)
    response = await DB.read(settings.MESSAGE_COLLECTION)
    if not response or "status_code" in response:
        return None

    return response


async def get_room_messages(org_id: str, room_id: str) -> list:
    """Get all messages in a room
    Args:
        org_id (str): The organization id
        room_id (str): The room id

    Returns:
        dict: key value pair of message info mapped according to message schema
    """

    DB = DataStorage(org_id)
    response = await DB.read(settings.MESSAGE_COLLECTION, query={"room_id": room_id})

    return response or []


async def get_message(org_id: str, room_id: str, message_id: str) -> dict:
    """Get messages in a room
    Args:
        org_id (str): The organization id
        room_id (str): The room id
        message_id (str): The message id
    Returns:
        dict: key value pair of message info mapped according to message schema
    """
    DB = DataStorage(org_id)
    query = {"room_id": room_id, "_id": message_id}
    response = await DB.read(settings.MESSAGE_COLLECTION, query=query)
    if response and "status_code" not in response:
        return response
    return {}
