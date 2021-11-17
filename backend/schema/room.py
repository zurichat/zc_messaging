from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from fastapi import HTTPException
from pydantic import BaseModel, root_validator


class Role(str, Enum):
    """
    Enum for the roles of a user in a room.
    """

    ADMIN = "admin"
    MEMBER = "member"


class Plugin(str, Enum):
    """
    Provides list of choices for plugin name
    """

    DM = "DM"
    CHANNEL = "Channel"


class RoomMember(BaseModel):
    """Describes the nested object
    content of the room_member variable
    """

    role: Role
    starred: bool = False
    closed: Optional[bool] = False


class Room(BaseModel):
    """Describes the request model for creating
    new room
    """

    org_id: str
    plugin_name: Plugin
    plugin_id: str
    room_name: Optional[str]
    created_at: str = str(datetime.now())
    room_members: Dict[str, RoomMember]
    is_default: bool = False
    is_private: bool = True
    archived: bool = False

    @root_validator(pre=True)
    @classmethod
    def check_group_dm(cls, values):
        """
        Checks if the plugin_name is group_dm
        """
        if (
            values["plugin_name"] == Plugin.DM.value
            and len(list(values.get("room_members", {}).keys())) > 9
        ):
            raise HTTPException(
                status_code=400, detail="Group DM cannot have more than 9 members"
            )
        return values
