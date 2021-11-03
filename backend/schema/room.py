from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class RoomMember(BaseModel):
    """Describes the nested object
    content of the room_member variable
    """

    role: str
    starred: bool = False
    closed: Optional[bool] = False


class Room(BaseModel):
    """Describes the request model for creating
    new room
    """

    org_id: str
    plugin_name: str
    plugin_id: str
    room_name: Optional[str]
    created_at: str = str(datetime.now())
    room_members: Dict[str, RoomMember]
    is_default: bool = False
    is_private: bool
    archived: bool = False
