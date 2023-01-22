from pydantic import BaseModel
from datetime import datetime


class ThreadData(BaseModel):
    sender_id: str
    message: str
    created_at: datetime

class ThreadResponse(BaseModel):
    status: int
    event: str
    thread_id: str
    room_id: str
    message_id: str
    data: ThreadData
