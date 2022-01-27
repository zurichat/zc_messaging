from typing import Any, Dict, List, Optional

import requests
from config.settings import settings
from fastapi import status
from fastapi.exceptions import HTTPException


class DataStorage:
    """Serves as a layer of abstraction for communication between zc_messaging
    data and the database on zc_core.

    It uses API endpoints from zc_core to perform CRUD operations on zc_messaging
    collection data.

    Attributes:
        write_api str): Zc_core API endpoint for writing (POST) and updating (PUT) data.
        read_api (str): Zc_core API endpoint for reading data.
        delete_api (str): Zc_core API endpoint for deleting data.
        get_members_api (str): Zc_core API endpoint for getting members of an organization.
        organization_id (str): The organization id where the operations are to be performed.
        plugin_id (str): The zc_messaging plugin id in the plugins marketplace.

    """

    def __init__(self, organization_id: str) -> None:
        """Initializes the data storage instance with zc_messaging plugin id.

        A request is sent to the plugins marketplace API endpoint on zc_core to get
        the plugin id.

        Args:
            organization_id: The organization id where the operations are to be performed.

        Raises:
            HTTPException: {"detail": "Request Timeout"}
        """
        self.write_api = f"{settings.BASE_URL}/data/write"
        self.read_api = f"{settings.BASE_URL}/data/read"
        self.delete_api = f"{settings.BASE_URL}/data/delete"
        self.get_members_api = (
            f"{settings.BASE_URL}/organizations/{organization_id}/members/"
        )
        self.organization_id = organization_id

        try:
            response = requests.get(url=f"{settings.BASE_URL}/marketplace/plugins")
            plugins = response.json().get("data").get("plugins")
            plugin = next(
                item for item in plugins if settings.PLUGIN_KEY in item["template_url"]
            )
            self.plugin_id = plugin.get("id")
        except requests.exceptions.RequestException as exception:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request Timeout"
            ) from exception

    async def write(self, collection_name: str, data: Dict[str, Any]) -> Any:
        """Writes data to zc_messaging collections.

        Calls the zc_core write endpoint (POST) and writes `data` to `collection_name`.

        Args:
            collection_name (str): The name of the collection where to write `data`.
            data (dict): The actual data the plugin wants to store.

        Returns:
            On success, a dict containing the success status and
            how many documents were successfully written.

            {
                    "status": 200,
                    "message": "success",
                    "data": {
                            "insert_count": 1,
                            "object_id": "61efec7365934b58b8e5d26b"
                    }
            }

            In case of error:

            {
                "status_code": 4xx|5xx,
                "message":
                    {
                        "status": 4xx|5xx,
                        "message": 'error occurred'
                    }
            }

        Raises:
            RequestException: Unable to connect to zc_core
        """

        body = {
            "plugin_id": self.plugin_id,
            "organization_id": self.organization_id,
            "collection_name": collection_name,
            "payload": data,
        }

        try:
            response = requests.post(url=self.write_api, json=body)
        except requests.exceptions.RequestException as exception:
            print(exception)
            return None
        if response.status_code == 201:
            return response.json()
        return {"status_code": response.status_code, "message": response.json()}

    async def update(
        self, collection_name: str, document_id: str, data: Dict[str, Any]
    ) -> Any:
        """Updates data to zc_messaging collections.

        Calls the zc_core write endpoint (PUT) and updates a specific `document_id` with `data`.

        Args:
            collection_name (str): The name of the collection where to update `document_id`
            document_id (str): The document id that will be updated.
            data (dict): The new data the plugin wants to store.

        Returns:
            On success, a dict containing the success status and
            how many documents were successfully updated.

            {
                    "status": 200,
                    "message": "success",
                "data": {
                    "matched_documents": 1,
                    "modified_documents": 1
                }
            }

            In case of error:

            {
                    "status": 200,
                    "message": "success",
                "data": {
                    "matched_documents": 0,
                    "modified_documents": 0
                }
            }

        Raises:
            RequestException: Unable to connect to zc_core
        """

        body = {
            "plugin_id": self.plugin_id,
            "organization_id": self.organization_id,
            "collection_name": collection_name,
            "object_id": document_id,
            "payload": data,
        }

        try:
            response = requests.put(url=self.write_api, json=body)
        except requests.exceptions.RequestException as exception:
            print(exception)
            return None
        if response.status_code == 200:
            return response.json()
        return {"status_code": response.status_code, "message": response.json()}

    async def read(
        self,
        collection_name: str,
        resource_id: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Reads data from zc_messaging collections.

        Calls the zc_core read endpoint (POST) and reads data with the option
        to filter and add mofifiers.

        Args:
            collection_name (str): The name of the collection where to read `data`.
            resource_id (str): The specific document id to be read.
            query (dict): An object that contains fields and their values
            to match documents.
            options (dict): An object that contains query results modifiers
            (limit, sort, skip, projection).

        Returns:
            On success, a dict containing the success status and
            the data as a list if no document id has been specified,
            otherwise a single object is returned.

            {
                "status": 200,
                "message": "success",
                "data": [
                    {...},
                    {...},
                    {...},
                    ...
                ]
            }

            In case of error:

            {
                "status": 200,
                "message": "success",
                "data": null
            }

        Raises:
            RequestException: Unable to connect to zc_core
        """

        body = {
            "plugin_id": self.plugin_id,
            "organization_id": self.organization_id,
            "collection_name": collection_name,
            "object_id": resource_id,
            "filter": query,
            "options": options,
        }

        try:
            response = requests.post(url=self.read_api, json=body)
        except requests.exceptions.RequestException as exception:
            print(exception)
            return None
        if response.status_code == 200:
            return response.json().get("data")
        return {"status_code": response.status_code, "message": response.reason}

    async def delete(self, collection_name: str, document_id: str):
        """Delete data from zc_messaging collections.

        Calls the zc_core delete endpoint (POST) and deletes the data matching `document_id`.

        Args:
            collection_name (str): The name of the collection where to delete the document.
            document_id (str):  The specific document id to be deleted.

        Returns:
            On success, a dict containing the success status and
            and how many documents were successfully deleted.

            {
                "status": 200,
                "message": "success",
                "data": {
                    "deleted_count": 1
                }
            }

            In case of error:

            {
                "status": 200,
                "message": "success",
                "data": {
                    "deleted_count": 0
                }
            }

        Raises:
            RequestException: Unable to connect to zc_core
        """

        body = {
            "plugin_id": self.plugin_id,
            "organization_id": self.organization_id,
            "collection_name": collection_name,
            "object_id": document_id,
        }

        try:
            response = requests.post(url=self.delete_api, json=body)
        except requests.exceptions.RequestException as exception:
            print(exception)
            return None
        if response.status_code == 200:
            return response.json()
        return {"status_code": response.status_code, "message": response.reason}

    async def get_all_members(self) -> Optional[List[Dict[str, Any]]]:
        """Gets a list of all members registered in an organisation.
        Calls the zc_core endpoint(GET) and retrieves the list of all members
        for a specific organization id.
        The organization id is passed in `get_members_api`.

        Returns:
            On success, a list containing the success status and
            and the organization's members.

            {
                "status": 200,
                "message": "Members retrieved successfully",
                "data": [
                    {
                        "_id": "619ba4671a5f54782939d385",
                        "bio": "",
                        "deleted": false,
                        "deleted_at": "0001-01-01T00:53:28+00:53",
                        "display_name": "",
                        "email": "member@gmail.com",
                        "files": null,
                        "first_name": "",
                        "id": "",
                        "image_url": "https://api.zuri.chat/files/profile_image/"
                        "619ba4671a5f54782939d384/619ba4671a5f54782939d385/20211213192712_0.png",
                        "joined_at": "2021-11-22T15:08:39.876+01:00",
                        "language": "",
                        "last_name": "",
                        "org_id": "619ba4671a5f54782939d384",
                        "phone": "",
                        "presence": "true",
                        ...
                    }
                ]
            }

        Raises:
            RequestException: Unable to connect to zc_core
        """

        url = self.get_members_api.format(org_id=self.organization_id)
        try:
            response = requests.get(url=url)
        except requests.exceptions.RequestException as exception:
            print(exception)
            return []
        if response.status_code == 200:
            return response.json().get("data")

    async def get_member(
        self, members: List[Dict[str, Any]], member_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get the information of a single registered member in an organisation.

        Args:
            members (list[dict]): The list of all members registered in an organization.
            member_id (str): The member's id.

        Returns:
            A dict containg the member's information.

            {
                "_id": "619ba4671a5f54782939d385",
                "bio": "",
                "deleted": false,
                "deleted_at": "0001-01-01T00:53:28+00:53",
                "display_name": "",
                "email": "member@gmail.com",
                "files": null,
                "first_name": "",
                "id": "",
                ...
            }
        """

        if members:
            for member in members:
                return member if member["_id"] == member_id else {}
