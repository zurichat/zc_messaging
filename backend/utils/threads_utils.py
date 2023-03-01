import uuid
from datetime import datetime
from typing import Any

from config.settings import settings
from fastapi import HTTPException, status
from schema.message import Thread
from utils.db import DataStorage
from utils.message_utils import get_message, update_message

# List all messages in a thread


async def get_message_threads(org_id, room_id, message_id):
    """Retrives all the messages in a thread.

    Args:
        org_id (str): The organization id where the message is being updated.
        room_id (str): The id of the room the message was sent in.
        message_id (str): The id of the message to be edited.


    Returns:
        [dict]: Returns an array of message objects.
    """

    # fetch message parent of the thread
    message = await get_message(org_id, room_id, message_id)
    return message["threads"]

async def get_message_thread(org_id, room_id, message_id, thread_id):
    """Retrives a single the messages in a thread.

    Args:
        org_id (str): The organization id where the message is being updated.
        room_id (str): The id of the room the message was sent in.
        message_id (str): The id of the parent message whose thead message is to be edited.
        thread_id (str): The id of the thread to be edited.


    Returns:
        [dict]: Returns an array of thread message objects.
    """

    query = {
        "_id": message_id,
        "threads.thread_id": thread_id
    }

    options = { "projection": {"threads.$": 1} }

    response = await DataStorage(org_id).read(
        collection_name=settings.MESSAGE_COLLECTION,
        query=query,
        options=options
    )
    
    if not response or "status_code" in response:
        return []

    return response["threads"]



async def add_message_to_thread_list(org_id, room_id, message_id, request: Thread):
    """Adds a message to a thread.

    Args:
        org_id (str): The organization id where the message is being updated.
        room_id (str): The id of the room the message was sent in.
        message_id (str): The id of the message to be edited.
        request (dict[str,any]): A new message object, to be added to the thread.

    Returns:
        dict[str, Any]: Returns an update success response.
    """

    # add message to a parent thread
    message = await get_message(org_id, room_id, message_id)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )
    del message["_id"]

    thread_message = request.dict(exclude_unset=True)
    thread_message["thread_id"] = str(uuid.uuid1())
    thread_message["created_at"] = str(datetime.utcnow())

    message["threads"].insert(0, thread_message)

    response = await update_message(org_id, message_id, message)

    return response, thread_message


async def update_message_thread(
    org_id, room_id, message_id, thread_id, payload: Thread
) -> dict[str, Any]:
    """Updates a message document in the database.
    Args:
        org_id (str): The organization id where the message is being updated.
        message_id (str): The id of the parent message whose thread message is to be edited.
        thread_id (str): The id of the thread message to be edited
        payload (dict[str, Any]): the new thread mesage
    Returns:
        dict[str, Any]: The response returned by DataStorage's update method.
    """
    message = await get_message(org_id, room_id, message_id)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parent message not found"
        )

    loaded_message_thread = await get_message_thread(org_id, room_id, message_id, thread_id)   


    if loaded_message_thread[0]["sender_id"] != payload["sender_id"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to edit this thread message",
        )

    payload["edited"] = True
    payload["thread_id"] = thread_id

    raw_query = {
        "$set": {"threads.$": payload},
    }

    query = {
        "_id": message_id,
        "threads.thread_id": thread_id,
    }
    
    return await DataStorage(org_id).update(
        collection_name=settings.MESSAGE_COLLECTION,
        raw_query=raw_query,
        query=query
    )
