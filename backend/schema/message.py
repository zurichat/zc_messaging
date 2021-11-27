from datetime import datetime
from typing import List

from pydantic import AnyHttpUrl, BaseModel


class Reaction(BaseModel):
    """Provides the nested object for reactions to message"""

    sender_id: str
    character: str


class Thread(BaseModel):
    """
    Provides a base model for all threads
    """

    sender_id: str
    room_id: str
    text: str
    reactions: List[Reaction] = []
    files: List[AnyHttpUrl] = []
    saved_by: List[str] = []
    is_pinned: bool = False
    is_edited: bool = False
    created_at: str = str(datetime.utcnow())


class Message(Thread):
    """Provides a base model for messages

    Message inherits from Thread
    and adds a field for list of threads
    """

    threads: List[Thread] = []
