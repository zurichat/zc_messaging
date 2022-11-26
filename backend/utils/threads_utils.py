from http.client import HTTPException
import json
from typing import Any, Optional
from schema.message import Thread
from schema.message import Message, MessageRequest

from utils.db import DataStorage
from utils.message_utils import get_message ,update_message
from config.settings import settings

# List  all messages in a thread

async def get_messages_in_thread(org_id, room_id, message_id):
    """Retrives all the messages in a thread.

    Args:
        org_id (str): The organization id where the message is being updated.
        room_id (str): The id of the room the message was sent in.
        message_id (str): The id of the message to be edited.
        

    Returns:
        [dict]: Returns an array of message objects.
    """

    # fetch message parent of the thread
    DB = DataStorage(org_id)
    messages = await get_message(org_id, room_id, message_id)
    return messages["threads"]



async def add_message_to_thread(org_id, room_id, message_id, request):
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

    payload = request.dict(exclude_unset=True)

    del message["_id"]

    thread= message["threads"]
    thread.append(payload)
   
    response = await update_message(org_id, message_id, message)
    
    return response

