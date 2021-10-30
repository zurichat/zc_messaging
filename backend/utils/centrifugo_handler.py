from enum import Enum
from typing import Any, Dict, Optional

import httpx

CENTRIFUGO_HOST = "https://realtime.zuri.chat/api"
CENTRIFUGO_API_TOKEN = "58c2400b-831d-411d-8fe8-31b6e337738b"


class Events(Enum):
    """
    An enumeration of all events to be used in centrifugo
    """

    MESSAGE_CREATE = "message_create"
    MESSAGE_UPDATE = "message_update"
    MESSAGE_DELETE = "message_delete"
    ROOM_CREATE = "room_create"
    ROOM_UPDATE = "room_update"
    ROOM_DELETE = "room_delete"
    ROOM_MEMBER_ADD = "room_member_add"
    ROOM_MEMBER_REMOVE = "room_member_remove"
    SIDEBAR_UPDATE = "sidebar_update"

    def __str__(self) -> str:
        return str.__str__(self)


class CentrifugoHandler:
    """A helper class to handle communication with the Centrifugo server."""

    def __init__(self) -> None:
        """Initialize CentrifugoHandler with `address` and `api_key` values."""
        self.address = CENTRIFUGO_HOST
        self.api_key = CENTRIFUGO_API_TOKEN

        self.headers = {
            "Content-type": "application/json",
            "Authorization": "apikey " + self.api_key,
        }

    async def _send_command(self, command: Dict[str, Any]) -> Dict[int, Any]:
        """Connects to the Centrifugo server and sends command to execute via Centrifugo Server API.

            Args:
                command (Dict[int, Any]): The command to be sent to Centrifugo

            Raises:
                RequestException: There was an ambiguous exception that occurred while handling the
        request

            Returns:
                Dict[int, Any]: The response from Centrifugo after executing the command sent
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=self.address, json=command, headers=self.headers
                )
                print(response)
                return {"status_code": response.status_code, "message": response.json()}
            # response = requests.post(
            #     url=self.address, headers=self.headers, json=command
            # )
            # return {"status_code": response.status_code, "message": response.json()}
        except httpx.RequestError as error:
            raise httpx.RequestError(error) from error

    async def publish(
        self,
        room: str,
        event: Events,
        data: Dict[str, str],
        plugin_url: str = "messaging.zuri.chat",
    ) -> Dict[str, Any]:
        """Publish data into a room.

        Args:
            room (str): The name of the room where to publish the data
            event (Events): Event enum obj associated with the data being published
            data (Dict[str, str]): Custom JSON data to publish into the room
            plugin_url (str): The plugin url to where the data will be used

        Returns:
            Dict[str, Any]: The formatted response after executing the command sent
        """
        data_publish = {
            "status": 200,
            "event": event.value,
            "plugin_url": plugin_url,
            "data": data,
        }

        command = {
            "method": "publish",
            "params": {
                "channel": room,
                "data": data_publish,
            },
        }
        try:
            response = await self._send_command(command)
        except httpx.RequestError:
            return {"status": 400, "message": "Invalid Request"}
        else:
            if response and response.get("status_code") == 200:
                return data_publish
            return {"status": 424, "message": "centrifugo failed"}

    async def unsubscribe(
        self, user: str, room: str, client: Optional[str] = None
    ) -> None:
        """Unsubscribe a user from a room

        Args:
            user (str): The id of a user inside the current room
            room (str): The name of the room where to unsubscribe the user
            client (Optional[str]) Specific client ID to unsubscribe. Defaults to None.

        Returns:
            [type]: The response from Centrifugo after executing the command sent
        """

        command = {
            "method": "unsubscribe",
            "params": {"channel": room, "user": user, "client": client},
        }
        try:
            response = await self._send_command(command)
        except httpx.RequestError:
            return {"status": 400, "message": "Invalid Request"}
        else:
            if response and response.get("status_code") == 200:
                return {
                    "status": 200,
                    "event": "unsubscribe",
                    "data": {"user": user, "room": room},
                }
            return {"status": 424, "message": "centrifugo failed"}


# An instance of CentrifugoHandler
# This will be used when importing the class
centrifugo_client = CentrifugoHandler()
