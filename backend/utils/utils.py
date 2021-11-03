import requests
from db_handler import DataStorage

helper = DataStorage()


async def get_rooms(member_id, org_id):
    """Get the rooms a user is in
    Args:
        member_id (str): The user id
    Returns:
        [List]: [description]
    """

    helper.organization_id = org_id
    query = {"room_members": member_id}
    options = {"sort": {"created_at": -1}}
    response = await helper.read("rooms", query=query, options=options)

    if response and "status_code" not in response:
        return response
    return []


async def get_all_organization_members(org_id: str):
    """Gets a list of all members registered in an organisation
    Args:
        org_id (str): The organization's id
    Returns:
        [List]: [list of objects]
    """
    try:
        response = requests.get(
            f"https://api.zuri.chat/organizations/{org_id}/members/"
        )
        if response.status_code == 200:
            return response.json()["data"]
    except requests.exceptions.RequestException as exception:
        print(exception)
        return list


async def get_member(members: list, member_id: str):
    """Get info of a registered member in an organisation
    Args:
        org_id (str): The organization's id,
        member_id (str): The member's id
    Returns:
        {dict}: {dict containing user info}
    """
    for member in members:
        if member["_id"] == member_id:
            return member
    return dict


async def sidebar_emitter(
    org_id, member_id, category: str, group_name: str
):  # group_room_name = None or a String of Names
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

    rooms = []
    starred_rooms = []
    user_rooms = await get_rooms(member_id=member_id, org_id=org_id)
    members = await get_all_organization_members(org_id)

    if user_rooms is not None:
        for room in user_rooms:
            room_profile = {}
            if len(room["room_user_ids"]) == 2:
                room_profile["room_id"] = room["_id"]
                room_profile["room_url"] = f"/dm/{room['_id']}"
                user_id_set = set(room["room_user_ids"]).difference({member_id})
                partner_id = list(user_id_set)[0]

                profile = await get_member(members, partner_id)

                if "user_name" in profile and profile["user_name"] != "":
                    if profile["user_name"]:
                        room_profile["room_name"] = profile["user_name"]
                    else:
                        room_profile["room_name"] = "no user name"
                    if profile["image_url"]:
                        room_profile["room_image"] = profile["image_url"]
                    else:
                        room_profile["room_image"] = (
                            "https://cdn.iconscout.com/icon/free/png-256/"
                            "account-avatar-profile-human-man-user-30448.png"
                        )

                else:
                    room_profile["room_name"] = "no user name"
                    room_profile["room_image"] = (
                        "https://cdn.iconscout.com/icon/free/png-256/"
                        "account-avatar-profile-human-man-user-30448.png"
                    )
            else:
                room_profile["room_name"] = room["room_name"]
                room_profile["room_id"] = room["_id"]
                room_profile["room_url"] = f"/dm/{room['_id']}"

            rooms.append(room_profile)

            if room["room_members"]["starred"] is True:
                starred_rooms.append(room_profile)

    side_bar = {
        "event": "sidebar_update",
        "plugin_id": "messaging.zuri.chat",
        "data": {
            "name": "Messaging",
            "description": "Sends messages between users in a dm or channel",
            "plugin_id": "messaging.zuri.chat",
            "organisation_id": f"{org_id}",
            "user_id": f"{member_id}",
            "group_name": f"{group_name}",
            "category": f"{category}",
            "show_group": False,
            "button_url": f"/{category}",
            "public_rooms": [],
            "starred_rooms": starred_rooms,
            "joined_rooms": rooms,
        }
        # List of rooms/channels created whenever a user starts a DM chat with another user
        # This is what will be displayed by Zuri Main
    }
    return side_bar
