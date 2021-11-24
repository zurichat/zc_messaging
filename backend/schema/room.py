import asyncio
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, root_validator
from utils.room_utils import get_org_rooms


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


class RoomType(str, Enum):
    """Provides choices of plugins.

    Provides class level constants for the plugins.
    DM ['DM'] -> direct message plugin
    CHANNEL ['Channel'] -> channel plugin
    """

    DM = "DM"
    GROUP_DM = "GROUP_DM"
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

    id: str = Field(None, alias="_id")
    org_id: str
    room_name: str
    room_type: RoomType
    room_members: Dict[str, RoomMember]
    created_at: str = str(datetime.utcnow())
    created_by: str = None
    description: Optional[str] = None
    topic: Optional[str] = None
    is_default: bool = False
    is_private: bool = True
    is_archived: bool = False

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
        room_type = values.get("room_type")
        room_members = values.get("room_members", {})
        topic = values.get("topic")
        description = values.get("description")
        org_id = values.get("org_id")
        rooms = asyncio.run(get_org_rooms(org_id=org_id, room_type=room_type))

        if (
            room_type == RoomType.GROUP_DM
            and len(set(room_members.keys())) > 9
            and len(set(room_members.keys())) < 2
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group DM cannot have more than 9 unique members and less than 2 members",
            )

        if room_type == RoomType.DM and len(set(room_members.keys())) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DM can only have 2 unique members",
            )

        if room_type in (RoomType.GROUP_DM, RoomType.DM):
            for room in rooms:
                if set(room["room_members"].keys()) == set(room_members.keys()):
                    raise HTTPException(
                        status_code=status.HTTP_200_OK,
                        detail={
                            "message": "room already exists",
                            "room_id": room["room_id"],
                        },
                    )

        if room_type in (RoomType.GROUP_DM, RoomType.DM) and topic is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DM or Group DM should not have a topic",
            )

        if room_type in (RoomType.GROUP_DM, RoomType.DM) and description is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DM or Group DM should not have a description",
            )

        return values

    @root_validator(pre=True)
    @classmethod
    def validates_channels(cls, values):
        """Checks if the room_members has at least two unique members

        Args:
            values [dict]: key value pair of all room members

        Returns:
            [dict]: key value pair of all object

        Raises:
            HTTPException [400]: if room_members has less than two unique members
        """
        room_type = values.get("room_type")
        room_name = values.get("room_name")
        org_id = values.get("org_id")

        rooms = asyncio.run(get_org_rooms(org_id=org_id, room_type=room_type))

        if room_type == RoomType.CHANNEL and room_name.casefold() in [
            room["room_name"].casefold() for room in rooms
        ]:
            raise HTTPException(
                status_code=status.HTTP_200_OK, detail="room name already exist"
            )

        return values
