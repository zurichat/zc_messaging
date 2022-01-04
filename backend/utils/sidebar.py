from schema.room import RoomType
from utils.centrifugo import Events, centrifugo_client
from utils.db import DataStorage
from utils.room_utils import DEFAULT_DM_IMG, get_org_rooms


class Sidebar:
    """Serves as a data source for the sidebar

    Sidebar class helps makes faster connection to core,
    sorts out data, and creates the sidebar data format
    for the frontend
    """

    @classmethod
    async def __get_room_members(
        cls, member_id: str, room: dict, org_members: list, DB: DataStorage
    ) -> dict:
        """Gets the room members excluding the current user

        Args:
            member_id (str): member_id of the current user
            room (dict): room object data
            org_members (list): list of all members in the organization

        Returns:
            [dict]: key value pair of room members
                    example: {'4551b653461237': {
                                'username': 'xzenon',
                                'image_url': 'https://avatars.zuri.net/images/avatar_default.png',
                                'starred': True
                                'role': 'admin'
                                }
                            }
        """
        room_members = room.get("room_members")
        room_members.pop(member_id, "not-found")  # remove self from room members
        for room_member_id in room_members.keys():
            member_data = await DB.get_member(room_member_id, org_members)
            username = member_data.get("user_name", "no user name")
            image_url = member_data.get("image_url") or DEFAULT_DM_IMG
            room_members[room_member_id].update(username=username, image_url=image_url)
        return room_members

    @classmethod
    async def __get_dm_room_name(cls, room_members: dict) -> str:
        """Concatenates the room members names to create the room name

        Args:
            room_members (dict): key value pair of room members

        Returns: string representation of room name
        """
        user_names = [member["username"] for member in room_members.values()]
        return ",".join(user_names)

    @classmethod
    async def __get_dm_room_image_url(cls, room_members: dict) -> str:
        """Gets the room image url from the first member in the room

        Args:
            room_members (dict): key value pair of room members

        Returns:
            [str]: image url of the first member in the room
        """
        members = list(room_members.values())
        return members[0]["image_url"] if len(members) > 0 else DEFAULT_DM_IMG

    async def __get_room_profile(
        self, member_id: str, room: dict, org_members: list, DB: DataStorage
    ) -> dict:
        """Stores the room profile data for the sidebar

        Args:
            member_id (str): member_id of the current user
            room (dict): room object data
            org_members (list): list of all members in the organization

        Returns:
            dict: key value pair of room profile
        """
        room_profile = {}
        if room.get("room_type") in (RoomType.DM, RoomType.GROUP_DM):
            room_members = await self.__get_room_members(
                member_id, room, org_members, DB
            )
            room_profile["room_name"] = await self.__get_dm_room_name(room_members)
            room_profile["image_url"] = await self.__get_dm_room_image_url(room_members)

        else:
            room_profile["room_name"] = room["room_name"]
            room_profile["image_url"] = ""

        room_profile["room_id"] = room["_id"]
        room_profile["room_url"] = f"/{room['room_type'].lower()}/{room['_id']}"

        return room_profile

    async def __get_joined_rooms(
        self, member_id: str, user_rooms: list, org_members: list, DB: DataStorage
    ) -> dict:
        """Gets the profiles for all rooms for the sidebar

        Args:
            member_id (str): member_id of the current user
            user_rooms (list): list of all rooms of the current user
            org_members (list): list of all members in the organization

        Returns:
            dict: contains data as key value store of room profiles
            sample_data: {"rooms": list,
                          "starred_rooms":list
                          }
        """
        rooms = []
        starred_rooms = []
        user_rooms = user_rooms or []
        for room in user_rooms:
            if room.get("room_members").get(member_id).get("closed") is False:
                room_profile = await self.__get_room_profile(
                    member_id, room, org_members, DB
                )
                rooms.append(room_profile)
            if room.get("room_members").get(member_id, {}).get("starred"):
                starred_rooms.append(room_profile)
        return {"rooms": rooms, "starred_rooms": starred_rooms}

    async def __get_public_rooms(
        self, member_id: str, org_id: str, org_members: list, DB: DataStorage
    ) -> dict:
        """Gets the public rooms for the sidebar

        Args:
            member_id (str): member_id of the current user
            org_members (list): list of all members in the organization

        Returns:
            dict: contains data as key value store of room profiles
            sample_data: key value pair of room profile
        """
        rooms = []
        public_rooms = await get_org_rooms(org_id, is_private=False)
        if public_rooms:
            for room in public_rooms:
                room_profile = await self.__get_room_profile(
                    member_id, room, org_members, DB
                )
                rooms.append(room_profile)
        return rooms

    async def format_data(self, org_id: str, member_id: str, room_type: str) -> dict:
        """Get sidebar info of rooms a registered member belongs to.

        Args:
            org_id (str): The organization's id,
            member_id (str): The member's id,
            room_type (str): The room type.
        Returns:
            {dict}: {dict containing user info}
        """

        DB = DataStorage(org_id)
        room_type_query = room_type
        if room_type != RoomType.CHANNEL:
            room_type_query = {"$ne": RoomType.CHANNEL}

        user_rooms = await get_org_rooms(
            member_id=member_id, org_id=org_id, room_type=room_type_query
        )

        org_members = await DB.get_all_members()
        joined_rooms = await self.__get_joined_rooms(
            member_id, user_rooms, org_members, DB
        )
        public_rooms = (
            await self.__get_public_rooms(member_id, org_id, org_members, DB)
            if room_type == RoomType.CHANNEL
            else []
        )

        return {
            "name": "Channels" if room_type == RoomType.CHANNEL else "Direct Messages",
            "description": (
                "Sends messages between users in a channel"
                if room_type == RoomType.CHANNEL
                else "Sends direct messages between users"
            ),
            "plugin_id": "chat.zuri.chat",
            "organisation_id": f"{org_id}",
            "user_id": f"{member_id}",
            "group_name": f"{room_type}",
            "category": (
                "channels" if room_type == RoomType.CHANNEL else "direct messages"
            ),
            "show_group": False,
            "button_url": "/channels" if room_type == RoomType.CHANNEL else "/dm",
            "public_rooms": public_rooms,
            "starred_rooms": joined_rooms["starred_rooms"],
            "joined_rooms": joined_rooms["rooms"],
        }

    async def publish(self, org_id: str, member_id: str, room_type: str) -> dict:
        """Get sidebar info of rooms a registered member belongs to.

        Args:
            org_id (str): The organization's id,
            member_id (str): The member's id,
            room_type(str): category of the plugin (direct message or channel)

        Returns:
            {dict}: {dict containing centrifugo response}
        """
        sidebar_data = await self.format_data(org_id, member_id, room_type)

        room = f"{org_id}_{member_id}_sidebar"
        response = await centrifugo_client.publish(
            event=Events.SIDEBAR_UPDATE, data=sidebar_data, room=room
        )

        return response


sidebar = Sidebar()
