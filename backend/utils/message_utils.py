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
