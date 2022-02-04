from utils.db import DataStorage

MESSAGE_COLLECTION = "messages"


async def get_org_messages(org_id: str) -> list:
    """Get all messages in a room
    Args:
        org_id (str): The organization id

    Returns:
        dict: key value pair of message info mapped according to message schema
    """

    DB = DataStorage(org_id)
    response = await DB.read(MESSAGE_COLLECTION, {})
    if response and "status_code" not in response:
        return response
    return {}


async def get_room_messages(org_id: str, room_id: str) -> list:
    """Get all messages in a room
    Args:
        org_id (str): The organization id
        room_id (str): The room id

    Returns:
        dict: key value pair of message info mapped according to message schema
    """

    DB = DataStorage(org_id)
    response = await DB.read(MESSAGE_COLLECTION, query={"room_id": room_id})

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
    response = await DB.read(MESSAGE_COLLECTION, query=query)
    if response and "status_code" not in response:
        return response
    return {}


async def update_reaction(org_id: str, message: dict) -> dict:
    """Update message reactions
    Args:
        org_id (str): The organization id
        message_id (str): The message id
        message (dict): The data to update
    Returns:
        dict: key value pair of message info mapped according to message schema
    """
    DB = DataStorage(org_id)

    message_id = message["_id"]
    data = {"emojis": message["emojis"]}
    response = await DB.update(MESSAGE_COLLECTION, message_id, data)
    if response and "status_code" not in response:
        return response
    return {}


def toggle_reaction(emoji: dict, payload: dict, reactions: list) -> dict:
    """[summary]
    Args:
        emoji (dict): [description]
        payload (dict): [description]
        reactions (List[dict]): [description]
    Returns:
       emoji (dict): [description]
    """
    if payload.reactedUsersId[0] not in emoji["reactedUsersId"]:
        emoji["reactedUsersId"].append(payload.reactedUsersId[0])
        emoji["count"] += 1
    else:
        emoji["reactedUsersId"].remove(payload.reactedUsersId[0])
        emoji["count"] -= 1
        if emoji["count"] == 0:
            reactions.remove(emoji)
    return emoji


def get_member_emoji(emoji_name: str, emojis: list):
    """[summary]
    Args:
        emoji_name (str): [description]
        emojis (List[dict]): [description]
    Returns:
        [type]: [description]
    """
    if not emojis:
        return None
    for emoji in emojis:
        if emoji_name == emoji["name"]:
            return emoji
    return None
