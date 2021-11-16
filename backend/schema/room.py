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
    room_members: Dict[str, RoomMember]
    created_at: str = str(datetime.now())


class Channel(BaseModel):
    """Describes the request model for fields specific to
    a channel
    """

    description: Optional[str] = None
    topic: Optional[str] = None
    room_name: str
    is_default: bool = False
    is_private: bool = True
    archived: bool = False


class RoomResponse(BaseModel):
    """Describes the fields returned upon
    calling the create_room endpoint
    """

    room_id: str
