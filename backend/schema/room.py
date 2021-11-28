from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from fastapi import HTTPException
from pydantic import BaseModel, root_validator, validator


class Role(str, Enum):
    """Provides choices for the roles of a user in a room.

    ADMIN ['admin'] -> The admin role is the only one that can add or remove users from a room.
    MEMBER ['member'] -> The member role cannot add or remove users from a room
    """

    ADMIN = "admin"
    MEMBER = "member"

    def __str__(self):
        """returns string representation of enum choice"""
        return self.value


class Plugin(str, Enum):
    """Provides choices of plugins.

    Provides class level constants for the plugins.
    DM ['DM'] -> direct message plugin
    CHANNEL ['Channel'] -> channel plugin
    """

    DM = "DM"
    CHANNEL = "Channel"

    def __str__(self):
        """returns string representation of enum choice"""
        return self.value


class RoomMember(BaseModel):
    """Describes the nested object
    content of the room_member variable
    """

    role: Role
    starred: bool = False
    closed: Optional[bool] = False


class Room(BaseModel):
    """Describes the request model for creating new rooms."""

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
    def validate_dm(cls, values):
        """validates data required for a DM room
        Args:
            values [dict]: key value pair of all object data

        Returns:
            [dict]: key value pair of all object data

        Raises:
            HTTPException [400]: if group dm exceeds 9 members
            HTTPException [400]: if DM has topic
            HTTPException [400]: if DM has a description
        """
        plugin_name = values.get("plugin_name")
        room_members = values.get("room_members", {})
        topic = values.get("topic")
        description = values.get("description")
        created_by = values.get("created_by")

        if plugin_name == Plugin.DM and len(list(room_members.keys())) > 9:
            raise HTTPException(
                status_code=400, detail="Group DM cannot have more than 9 members"
            )

        if plugin_name == Plugin.DM and topic is not None:
            raise HTTPException(status_code=400, detail="DM should not have a topic")

        if plugin_name == Plugin.DM and description is not None:
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
    def validates_room_members(cls, value):
        """Checks if the room_members has at least two unique members

        Args:
            values [dict]: key value pair of all room members

        Returns:
            [dict]: key value pair of all object

        Raises:
            HTTPException [400]: if room_members has less than two unique members
        """
        if len(set(value.keys())) < 2:
            raise HTTPException(
                status_code=400, detail="Room must have at least 2 unique members"
            )

        return value


class AddToRoom(BaseModel):
    """a schema that defines the request params for adding members to a room"""

    new_member: Dict[str, RoomMember]
