from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from fastapi import HTTPException
from pydantic import BaseModel, root_validator, validator


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
    room_members: Dict[str, RoomMember]
    created_at: str = str(datetime.now())
    created_by: str = None
    description: Optional[str] = None
    topic: Optional[str] = None
    room_name: str
    is_default: bool = False
    is_private: bool = True
    archived: bool = False

    @root_validator(pre=True)
    @classmethod
    def check_group_dm(cls, values):
        """
        Checks if the plugin_name is group_dm
        """
        plugin_name = values.get("plugin_name")
        room_members = values.get("room_members", {})
        topic = values.get("topic")
        description = values.get("description")
        created_by = values.get("created_by")

        if plugin_name == Plugin.DM.value and len(list(room_members.keys())) > 9:
            raise HTTPException(
                status_code=400, detail="Group DM cannot have more than 9 members"
            )

        if plugin_name == Plugin.DM.value and topic is not None:
            raise HTTPException(status_code=400, detail="DM should not have a topic")

        if plugin_name == Plugin.DM.value and description is not None:
            raise HTTPException(
                status_code=400, detail="DM should not have a description"
            )

        if plugin_name == Plugin.DM.value and created_by is not None:
            raise HTTPException(
                status_code=400, detail="DM should not have a created by"
            )

        return values

    @validator("room_members", always=True)
    @classmethod
    def check_room_members(cls, value):
        """
        Checks if the room_members has at least two members
        """
        if len(list(value.keys())) < 2:
            raise HTTPException(
                status_code=400, detail="Room must have at least 2 members"
            )

        return value
