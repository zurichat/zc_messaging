from typing import Any, Optional

from config.settings import settings
from utils.db import DataStorage


async def get_org_messages(org_id: str) -> Optional[list[dict[str, Any]]]:
    """Gets all messages sent in  an organization.

    Args:
        org_id (str): The organization id

    Returns:
        list[dict]: A list of key value pairs of messages info mapped according to message schema.

        [
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
        ]
    """

    DB = DataStorage(org_id)
    response = await DB.read(settings.MESSAGE_COLLECTION)

    if not response or "status_code" in response:
        return None

    return response


async def get_room_messages(
    org_id: str, room_id: str
) -> Optional[list[dict[str, Any]]]:
    """Gets all messages sent inside  a room.
    Args:
        org_id (str): The organization id
        room_id (str): The room id

    Returns:
        list[dict]: A list of key value pairs of messages info mapped according to message schema.

        [
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
        ]
    """

    DB = DataStorage(org_id)
    response = await DB.read(settings.MESSAGE_COLLECTION, query={"room_id": room_id})

    if response is None:
        return []

    if "status_code" in response:
        return None

    return response


async def get_message(
    org_id: str, room_id: str, message_id: str
) -> Optional[dict[str, Any]]:
    """Get a specific message in a room.

    Args:
        org_id (str): The organization id
        room_id (str): The id of the room where the message is to be retrieved.
        message_id (str): The id of the message to be retrieved.

    Returns:
        dict: key value pair of the message info mapped according to message schema.

        {
            "_id": "61eff23565934b58b8e5d26f",
            "created_at": "2022-01-24 18:05:01.129393",
            "edited": false,
            "emojis": [],
            "files": [],
            "org_id": "619ba4671a5f54782939d384",
            ...,
            "room_id": "61e72d1265934b58b8e5d220",
            "saved_by": [],
            "sender_id": "61e59f1b65934b58b8e5d1cb",
            "threads": [],
            "timestamp": 0
        }
    """

    DB = DataStorage(org_id)
    query = {"room_id": room_id, "_id": message_id}
    response = await DB.read(settings.MESSAGE_COLLECTION, query=query)

    if not response or "status_code" in response:
        return {}

    return response
