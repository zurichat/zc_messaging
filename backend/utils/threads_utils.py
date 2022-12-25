import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
import json
from typing import Any, Optional
from schema.message import Thread
from schema.message import Message, MessageRequest
from datetime import datetime
from utils.db import DataStorage
from utils.message_utils import get_message, update_message
from config.settings import settings

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


async def update_thread_message(
    org_id: str, message_id: str, thread_id: str, payload: dict[str, Any], message: dict[str, Any]
) -> dict[str, Any]:
    """
     Updates a thread object in message["threads"] then updates the message document in the database.
     Args:
         org_id (str): The organization id where the message is being updated.
         message_id (str): The id of the message to be edited.
         thread_id (str): The id of the thread to be edited
         payload (dict[str, Any]): The new data.
         message (dict[str, Any]): The message to be edited that has been loaded from the database
     Returns:
         dict[str, Any]: The response returned by DataStorage's update method.
     """
    threads = message["threads"]  # a list of thread objects

    # to edit a thread object in the list of threads
    for index in range(len(threads)):

        if threads[index]["thread_id"] == thread_id and threads[index]["sender_id"] == payload["sender_id"]:
            threads[index] = payload
            threads[index]["edited"] = True

            del message["_id"]

            db = DataStorage(org_id)
            return await db.update(settings.MESSAGE_COLLECTION, message_id, message)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Thread message not found or sender is not authorised to edit this message"
    )
