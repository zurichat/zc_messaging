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

    # fetch message parent of the thread
    DB = DataStorage(org_id)
    messages = await get_message(org_id, room_id, message_id)
    threads = messages["threads"]

    return threads


async def add_message_to_thread(org_id, room_id, message_id, request):

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
   
    res = await update_message(org_id, message_id, message)
    print(res)
    return res

