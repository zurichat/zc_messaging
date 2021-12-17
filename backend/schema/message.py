import asyncio
import concurrent.futures
from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from pydantic import AnyHttpUrl, BaseModel, Field, root_validator
from utils.room_utils import get_room


class Reaction(BaseModel):
    """Provides the nested object for reactions to message"""

    sender_id: str
    character: str


class MessageRequest(BaseModel):
    """
    Provides a base model for all threads
    """

    text: str
    reactions: List[Reaction] = []
    files: List[AnyHttpUrl] = []
    saved_by: List[str] = []
    created_at: str = str(datetime.utcnow())


class Thread(MessageRequest):
    """Provide structure for the thread schema

    Class inherits from MessageRequest to hold
    data for the thread schema
    """

    sender_id: str
    room_id: str
    org_id: str
    message_id: str = Field(None, alias="_id")

    @root_validator(pre=True)
    @classmethod
    def validates_message(cls, values):
        """Checks if the room_id and sender_id are valid

        Args:
            values [dict]: key value pair of sender and room id

        Returns:
            [dict]: key value pair of all object

        Raises:
            HTTPException [404]: if room_id or sender_id is invalid
        """

        sender_id = values.get("sender_id")
        org_id = values.get("org_id")
        room_id = values.get("room_id")
        with concurrent.futures.ThreadPoolExecutor(1) as executor:
            future = executor.submit(asyncio.run, get_room(org_id, room_id))
            room = future.result()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room not available"
            )

        if sender_id not in set(room["room_members"]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="sender not a member of this room",
            )
        return values


class Message(Thread):
    """Provides a base model for messages

    Message inherits from Thread
    and adds a field for list of threads
    """

    threads: List[Thread] = []


class MessageUpdateRequest(BaseModel):
    """
    Provides a base model for all threads
    """

    text: str
    sender_id: str
    edited_at: str = str(datetime.utcnow())
