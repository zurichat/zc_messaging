from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, ValidationError, root_validator


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

    # @root_validator(always=True)
    # @classmethod
    # async def is_channel_exist(cls, values):
    #     """
    #     Checks if the plugin_name is channel
    #     """
    #     plugin_name = values.get("plugin_name")
    #     room_name = values.get("room_name")
    #     org_id = values.get("org_id")
    #     rooms = await get_org_rooms(org_id, plugin_name)

    #     if plugin_name == "channel" and room_name in [
    #         room["room_name"] for room in rooms
    #     ]:
    #         raise ValidationError("Channel with this name already exists")
    #     return values

    # @root_validator(always=True)
    # @classmethod
    # async def is_dm_exist(cls, values):
    #     """
    #     Checks if the plugin_name is dm
    #     """
    #     plugin_name = values.get("plugin_name")
    #     room_members = values.get("room_members", {})
    #     org_id = values.get("org_id")
    #     rooms = await get_org_rooms(org_id, plugin_name)

    #     if plugin_name == "dm" and set(room_members.keys()) in [
    #         set(room["room_members"].keys()) for room in rooms
    #     ]:
    #         raise ValidationError("DM already exists")
    #     return values

    @root_validator(always=True)
    @classmethod
    def check_group_dm(cls, values):
        """
        Checks if the plugin_name is group_dm
        """
        if (
            values["plugin_name"] == "dm"
            and len(values.get("room_members", {}).keys()) > 9
        ):
            raise ValidationError("Cannot have more than 9 users in a DM")
        return values
