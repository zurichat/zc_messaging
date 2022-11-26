import asyncio
import concurrent.futures
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from bson.objectid import ObjectId
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, root_validator
from schema.custom import ObjId
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
    CHANNEL = "CHANNEL"

    def __str__(self):
        """returns string representation of enum choice"""
        return self.value


class RoomMember(BaseModel):
    """Describes the nested object
    content of the room_member variable
    """

    role: Role = Role.MEMBER
    starred: bool = False
    closed: Optional[bool] = False

class UpdateRoomRequest(BaseModel):
    """Describes the request model for updating rooms."""

    room_name: Optional[str] = None
    description: Optional[str] = None
    topic: Optional[str] = None
    is_private: bool = False
    is_archived: bool = False

class RoomRequest(BaseModel):
    """Describes the request model for creating new rooms."""

    room_name: Optional[str] = None
    room_type: RoomType
    room_members: Dict[ObjId, RoomMember]
    created_at: str = str(datetime.utcnow())
    description: Optional[str] = None
    topic: Optional[str] = None
    is_private: bool = False
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
        if values["room_type"].upper() != RoomType.CHANNEL:
            room_type = values.get("room_type").upper()
            room_members = values.get("room_members", {})
            topic = values.get("topic")
            description = values.get("description")
            org_id = values.get("org_id")

            # runs the asynchronous get_org_rooms in a synchronous thread because
            # it is used in a synchronous function
            with concurrent.futures.ThreadPoolExecutor(1) as executor:
                future = executor.submit(
                    asyncio.run, get_org_rooms(org_id=org_id, room_type=room_type)
                )
                rooms = future.result()

            if rooms is None:  # check if connection is avaliable
                raise HTTPException(
                    status_code=status.HTTP_424_FAILED_DEPENDENCY,
                    detail="unable to read database",
                )

            if room_type == RoomType.GROUP_DM and (
                len(set(room_members.keys())) > 9 or len(set(room_members.keys())) < 3
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Group DM cannot have more than 9 and less than 2 unique members",
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
                                "room_id": room["_id"],
                            },
                        )

            if topic is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="DM or Group DM should not have a topic",
                )

            if description is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="DM or Group DM should not have a description",
                )

            values["is_private"] = True
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
        if values.get("room_type").upper() == RoomType.CHANNEL:
            room_type = values.get("room_type")
            room_name = values.get("room_name")
            org_id = values.get("org_id")

            # runs the asynchronous get_org_rooms in a synchronous thread because
            # it is used in a synchronous function
            with concurrent.futures.ThreadPoolExecutor(1) as executor:
                future = executor.submit(
                    asyncio.run, get_org_rooms(org_id=org_id, room_type=room_type)
                )
                rooms = future.result()

            if rooms is None:  # check if connection is available
                raise HTTPException(
                    status_code=status.HTTP_424_FAILED_DEPENDENCY,
                    detail="unable to read database",
                )

            if room_name is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Channel name is required",
                )

            if room_name.casefold() in [room["room_name"].casefold() for room in rooms]:
                raise HTTPException(
                    status_code=status.HTTP_200_OK, detail="room name already exist"
                )

        return values


class Room(RoomRequest):
    """Provide structure for the room schema

    Class inherits from RooomRequest to hold data for the room schema
    """

    id: str = Field(None, alias="_id")
    org_id: str
    created_by: str

    @root_validator(pre=True)
    @classmethod
    def is_object_id(cls, values):
        """validates if the id is a valid object id

        Args:
            values [dict]: key value pair of all object data

        Returns:
            [dict]: key value pair of all object data

        Raises:
            HTTPException [400]: if id is not a valid object id
        """
        if values.get("id") is not None:
            if not ObjectId.is_valid(values.get("id")):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="id is not a valid object id",
                )

        if not ObjectId.is_valid(values.get("org_id")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="org_id is not a valid object id",
            )

        if not ObjectId.is_valid(values.get("created_by")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="created_by is not a valid object id",
            )

        return values
