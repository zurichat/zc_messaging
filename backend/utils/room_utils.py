from db import COLLECTION_NAME, DB

DEFAULT_DM_IMG = (
    "https://cdn.iconscout.com/icon/free/png-256/"
    "account-avatar-profile-human-man-user-30448.png"
)


async def get_org_rooms(
    org_id: str,
    member_id: str = None,
    plugin: str = None,
    is_private: bool = None,
    is_default: bool = None,
) -> list:
    """Get all rooms in an organization

    Args:
        org_id (str): The organization id
        category (Optional(str): The category of the room (channel, dm)

    Returns:
        [List]: returns a list of all rooms within that organisation
    """
    DB.organization_id = org_id
    query = {"$and": [{"org_id": org_id}]}
    if member_id is not None:
        query["$and"].append({f"room_members.{member_id}": {"$exists": True}})
    if plugin is not None:
        query["$and"].append({"plugin_name": plugin})
    if is_private is not None:
        query["$and"].append({"is_private": is_private})
    if is_default is not None:
        query["$and"].append({"is_default": is_default})

    options = {"sort": {"created_at": -1}}
    response = await DB.read(COLLECTION_NAME, query=query, options=options)
    if response is None:
        return []
    if "status_code" not in response:
        return response
    return None


async def get_room(org_id: str, room_id: str) -> dict:
    """Get info of a room in the db
    Args:
        org_id (str): The organization id
        room_id (str): The room id
    Returns:
        dict: key value pair of room info mapped accored to room schema
    """
    DB.organization_id = org_id
    query = {"_id": room_id}
    options = {"sort": {"created_at": -1}}
    response = await DB.read("rooms", query=query, options=options)

    if response and "status_code" not in response:
        return response
    return {}


async def get_room_members(org_id: str, room_id: str) -> dict:
    """Get the members of a room

    Args:
        org_id (str): The organization's id
        room_id (str): The room id

    Returns:
        [Dict]: key value
    """
    DB.organization_id = org_id
    query = {"_id": room_id}
    options = {"sort": {"created_at": -1}, "projection": {"room_members": 1, "_id": 0}}
    response = await DB.read("rooms", query=query, options=options)
    if response and "status_code" not in response:
        return response.get("room_members", {})
    return {}


async def get_member_starred_rooms(org_id: str, member_id: str) -> list:
    """Get all starred rooms of a user

    Args:
        org_id (str): The organization id
        member_id (str): The user id

    Returns:
        [List]: list of rooms that are starred by the user
    """
    DB.organization_id = org_id
    query = {f"room_members.{member_id}.starred": True}
    options = {"sort": {"created_at": -1}}
    response = await DB.read("rooms", query=query, options=options)
    if response and "status_code" not in response:
        return response
    return []


async def is_user_starred_room(org_id: str, room_id: str, member_id: str) -> bool:
    """Checks if room is starred by user

    Args:
        org_id (str): The organization id
        member_id (str): The user id

    Returns:
        bool: returns True if room is starred by user else returns False

    Raise:
        ValueError: Room not found
    """
    DB.organization_id = org_id
    query = {"_id": room_id}
    response = await DB.read("rooms", query=query)
    if response and "status_code" not in response:
        return response["room_members"][member_id]["starred"]
    raise Exception("Room not found")


class Sidebar:
    """Serves as a data source for the sidebar

    Sidebar class helps makes faster connection to core,
    sorts out data, and creates the sidebar data format
    for the frontend
    """

    @classmethod
    async def __get_room_members(
        cls, member_id: str, room: dict, org_members: list
    ) -> dict:
        """gets the room members excluding the current user

        Args:
            member_id (str): member_id of the current user
            room (dict): room object data
            org_members (list): list of all members in the organization

        Returns:
            [dict]: key value pair of room members
                    example: {'member_id': {
                                'username': str
                                'image_url': str
                                'starred': bool
                                'role': str}
                            }
        """
        room_members = room["room_members"]
        room_members.pop(member_id)  # remove self from room members
        room_members_ids = room_members.keys()
        for room_member_id in room_members_ids:
            member_data = await DB.get_member(room_member_id, org_members)
            username = member_data["user_name"] or "no user name"
            image_url = member_data["image_url"] or DEFAULT_DM_IMG
            room_members[room_member_id].update(username=username, image_url=image_url)
        return room_members

    @classmethod
    def __get_dm_room_name(cls, room_members: dict) -> str:
        """concatenates the room members names to create the room name

        Args:
            room_members (dict): key value pair of room members

        Returns: string representation of room name
        """
        user_names = [member["username"] for member in room_members.values()]
        return ",".join(user_names)

    @classmethod
    async def __get_dm_room_image_url(cls, room_members: dict) -> str:
        """gets the room image url from the first member in the room

        Args:
            room_members (dict): key value pair of room members

        Returns:
            [str]: image url of the first member in the room
        """
        return list(room_members.values())[0]["image_url"]

    async def __get_room_profile(
        self, member_id: str, room: dict, org_members: list
    ) -> dict:
        """stores the room profile data for the sidebar

        Args:
            member_id (str): member_id of the current user
            room (dict): room object data
            org_members (list): list of all members in the organization

        Returns:
            dict: key value pair of room profile
        """
        room_profile = {}
        if room["plugin_name"] == "dm":
            room_members = await self.__get_room_members(member_id, room, org_members)
        room_profile["room_id"] = room["_id"]
        room_profile["room_url"] = f"/{room['plugin_name']}/{room['_id']}"
        room_profile["room_name"] = (
            await self.__get_dm_room_name(room_members)
            if room["plugin_name"] == "dm"
            else room["room_name"]
        )
        room_profile["image_url"] = (
            await self.__get_dm_room_image_url(room_members)
            if room["plugin_name"] == "dm"
            else ""
        )
        return room_profile

    async def __get_joined_rooms(
        self, member_id: str, user_rooms: list, org_members: list
    ) -> dict:
        """gets the profiles for all rooms for the sidebar

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
            room_profile = await self.__get_room_profile(member_id, room, org_members)
            rooms.append(room_profile)
            if room["room_members"].get(member_id, {}).get("starred", False) is True:
                starred_rooms.append(room_profile)
        return {"rooms": rooms, "starred_rooms": starred_rooms}

    async def __get_public_rooms(
        self, member_id: str, org_id: str, org_members: list
    ) -> dict:
        """gets the public rooms for the sidebar

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
                    member_id, room, org_members
                )
                rooms.append(room_profile)
        return rooms

    async def format(self, org_id: str, member_id: str, plugin: str) -> dict:
        """Get sidebar info of rooms a registered member belongs to.
        Args:
            org_id (str): The organization's id,
            member_id (str): The member's id,
            category (str): category of the plugin (direct message or channel)
            group_name: name of plugin
            room_name: title of the room if any
        Returns:
            {dict}: {dict containing user info}
        """

        DB.organization_id = org_id
        user_rooms = await get_org_rooms(
            member_id=member_id, org_id=org_id, plugin=plugin
        )
        org_members = await DB.get_all_members()
        rooms_data = await self.__get_joined_rooms(member_id, user_rooms, org_members)
        public_rooms = await self.__get_public_rooms(member_id, org_id, org_members)
        return {
            "data": {
                "name": "Messaging",
                "description": "Sends messages between users in a dm or channel",
                "plugin_id": "messaging.zuri.chat",
                "organisation_id": f"{org_id}",
                "user_id": f"{member_id}",
                "group_name": f"{plugin}",
                "category": "channels" if plugin == "Channel" else "direct messages",
                "show_group": False,
                "button_url": "/channels" if plugin == "Channel" else "/dm",
                "public_rooms": public_rooms,
                "starred_rooms": rooms_data["starred_rooms"],
                "joined_rooms": rooms_data["rooms"],
            }
        }


sidebar = Sidebar()
