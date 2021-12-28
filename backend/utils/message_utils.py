from datetime import datetime, timedelta

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
    if response and "status_code" not in response:
        return response
    return {}


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


# get all the messages in a particular room
async def get_all_room_messages(room_id, org_id):
    """[summary]

    Args:
        room_id ([type]): [description]
        org_id ([type]): [description]

    Returns:
        [type]: [description]
    """
    DB = DataStorage(org_id)
    options = {"sort": {"created_at": -1}}
    response = await DB.read(
        MESSAGE_COLLECTION, query={"room_id": room_id}, options=options
    )
    if response and "status_code" not in response:
        return response
    return []


# get all the messages in a particular room filtered by date
async def get_messages(room_id, org_id, date):
    """

    Args:
        room_id ([type]): [description]
        org_id ([type]): [description]
        date ([type]): [description]

    Returns:
        [type]: [description]
    """

    DB = DataStorage(org_id)
    req_date = datetime.strptime(date, "%d-%m-%Y")
    next_day = req_date + timedelta(days=1)
    options = {"sort": {"created_at": -1}}
    query = {
        "$and": [
            {"room_id": room_id},
            {"created_at": {"$gte": str(req_date), "$lt": str(next_day)}},
        ]
    }

    response = await DB.read(MESSAGE_COLLECTION, query=query, options=options)
    if response and "status_code" not in response:
        return response
    return []
