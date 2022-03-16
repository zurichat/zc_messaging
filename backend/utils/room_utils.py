from typing import Any, Optional
from utils.db import DataStorage
from config.settings import settings

DEFAULT_DM_IMG = (
    "https://cdn.iconscout.com/icon/free/png-256/"
    "account-avatar-profile-human-man-user-30448.png"
)


async def get_org_rooms(
    org_id: str,
    member_id: Optional[str] = None,
    room_type: Optional[str] = None,
    is_private: Optional[bool] = None,
    is_default: Optional[bool] = None,
) -> Optional[list[dict[str, Any]]]:
    """Get all rooms in an organization.

    The list of the rooms can be filtered based on the values passed to the parameters.

    Args:
        org_id (str): The organization id.
        member_id (str): The member id.
        room_type (str): The room's type (CHANNEL, DM, GROUP_DM).
        is_private (bool): Whether the room is a private room or not.
        id_default (bool): Whether the room is a default room or not.

    Returns:
        list[dict]: A list of key value pairs of rooms info mapped according to room schema.

        [
            {
                "_id": "61e59de865934b58b8e5d1c8",
                "org_id": "619ba4671a5f54782939d384",
                "room_members": {
                    "619ba4671a5f54782939d385": {
                        "closed": false,
                        "role": "admin",
                        "starred": false
                    }
                },
                "room_type": "DM",
                "topic": "",
                ...
            },
            {
                "_id": "61f483d965934b58b8e5d283",
                "created_by": "619ba4671a5f54782939d385",
                "is_private": true,
                "org_id": "619ba4671a5f54782939d384",
                "room_name": "619ba4671a5f54782939d385",
                "room_type": "DM",
                ...
            },
            ...
            ]
    """

    db = DataStorage(org_id)
    query = {"$and": [{"org_id": org_id}]}

    if member_id is not None:
        query["$and"].append({f"room_members.{member_id}": {"$exists": True}})
    if room_type is not None:
        query["$and"].append({"room_type": room_type})
    if is_private is not None:
        query["$and"].append({"is_private": is_private})
    if is_default is not None:
        query["$and"].append({"is_default": is_default})

    options = {"sort": {"created_at": -1}}
    response = await db.read(settings.ROOM_COLLECTION, query=query, options=options)

    if response is None:
        return []

    if "status_code" in response:
        return None

    return response


async def get_room(org_id: str, room_id: str) -> dict:
    """Get info of a room in the db
    Args:
        org_id (str): The organization id
        room_id (str): The room id
    Returns:
        dict: key value pair of room info mapped accored to room schema
    """
    DB = DataStorage(org_id)
    query = {"_id": room_id}
    options = {"sort": {"created_at": -1}}
    response = await DB.read(settings.ROOM_COLLECTION, query=query, options=options)

    if response and "status_code" not in response:
        return response
    return {}


async def get_room_members(org_id: str, room_id: str) -> dict:
    """Get the members of a room

    Args:
        org_id (str): The organization's id
        room_id (str): The room id

    Returns:
        [Dict]: key value
    """
    DB = DataStorage(org_id)
    query = {"_id": room_id}
    options = {"sort": {"created_at": -1}, "projection": {"room_members": 1, "_id": 0}}
    response = await DB.read(settings.ROOM_COLLECTION, query=query, options=options)
    if response and "status_code" not in response:
        return response.get("room_members", {})
    return {}


async def get_member_starred_rooms(org_id: str, member_id: str) -> list:
    """Get all starred rooms of a user

    Args:
        org_id (str): The organization id
        member_id (str): The user id

    Returns:
        [List]: list of rooms that are starred by the user
    """
    DB = DataStorage(org_id)
    query = {f"room_members.{member_id}.starred": True}
    options = {"sort": {"created_at": -1}}
    response = await DB.read(settings.ROOM_COLLECTION, query=query, options=options)
    if response and "status_code" not in response:
        return response
    return []


async def is_user_starred_room(org_id: str, room_id: str, member_id: str) -> bool:
    """Checks if room is starred by user

    Args:
        org_id (str): The organization id
        member_id (str): The user id

    Returns:
        bool: returns True if room is starred by user else returns False

    Raise:
        ValueError: Room not found
    """
    DB = DataStorage(org_id)
    query = {"_id": room_id}
    response = await DB.read(settings.ROOM_COLLECTION, query=query)
    if response and "status_code" not in response:
        return response["room_members"][member_id]["starred"]
    raise Exception("Room not found")


async def remove_room_member(org_id: str, room_data: dict, member_id: str) -> dict:
    """Removes a member from a room

    Args:
        org_id (str): The organization id
        room_data (dict): The room data
        member_id (str): The member id to be removed

    Raises:
        ValueError: user not found in room
        RequestException: zc core fails to remove user from room

    Returns:
        [dict]: sample response includes
            {
                "member_id":"1234567yrtrt"
                "room_id":"2312244dsdsd"
            },
    """
    DB = DataStorage(org_id)
    remove_member = room_data["room_members"].pop(member_id, "not_found")

    if remove_member == "not_found":
        raise ValueError("user not a member of the room")

    room_id = room_data["_id"]
    room_members = {"room_members": room_data["room_members"]}

    update_room = await DB.update(settings.ROOM_COLLECTION, room_id, room_members)

    if update_room is None or update_room.get("status_code") is not None:
        raise ConnectionError("unable to remove room member")

    return {"member_id": member_id, "room_id": room_id}
