import requests

PLUGIN_ID = "617db02f27c36150b422bc4d"
ORG_ID = "619ba4671a5f54782939d384"
ROOM_COLLECTION = "rooms"
BASE_URL = "https://staging.api.zuri.chat"


class DataStorage:
    """Serves as a layer for communication for plugin data and server

    Provides a layer of abstraction for communication between plugin
    data and the database on zc_core

    """

    def __init__(
        self, plugin_id: str = PLUGIN_ID, organization_id: str = ORG_ID
    ) -> None:
        self.write_api = f"{BASE_URL}/data/write"
        self.delete_api = f"{BASE_URL}/data/delete"
        self.read_query_api = f"{BASE_URL}/data/read"
        self.get_member_api = f"{BASE_URL}/organizations/" + "{org_id}/members/"
        self.plugin_id = plugin_id
        self.organization_id = organization_id

    async def write(self, collection_name, data):
        """Function to write into db

        Args:
            collection_name (str): Name of Collection
            data (dict): payload

        Returns:
            None; cannot connect to db
            data: list; on success
            data: dict; on api call fails or errors
        """
        body = dict(
            plugin_id=self.plugin_id,
            organization_id=self.organization_id,
            collection_name=collection_name,
            payload=data,
        )
        try:
            response = requests.post(url=self.write_api, json=body)
        except requests.exceptions.RequestException as exception:
            print(exception)
            return None
        if response.status_code == 201:
            return response.json()

        return {"status_code": response.status_code, "message": response.reason}

    async def update(self, collection_name, document_id, data):
        """Function to update data from db.

        Args:
            collection_name (str): Name of collection
            Document_ID (str): Resource ID
            data (dict): payload
        Returns:
            None; cannot connect to db
            data: json object; on success
            data: dict; on api call fails or errors
        """
        body = dict(
            plugin_id=self.plugin_id,
            organization_id=self.organization_id,
            collection_name=collection_name,
            object_id=document_id,
            payload=data,
        )
        try:
            response = requests.put(url=self.write_api, json=body)
        except requests.exceptions.RequestException as exception:
            print(exception)
            return None
        if response.status_code == 200:
            return response.json()

        return {"status_code": response.status_code, "message": response.reason}

    # NB: refactoring read_query into read, DB.read now has functionality of read and read_query
    async def read(
        self,
        collection_name: str,
        query: dict,
        options: dict = None,
        resource_id: str = None,
    ):
        """
        Function to read data flexibly from db, with the option to query, filter and more
        Args:
            Collection_name (str): Name of COllection,
            Resource_id (str): Document ID,
            query (dict): Filter query
            options (dict):
        Returns:
            None: cannot connect to db
            data: list; on success
            data: dict; on api call fails or errors
        """
        request_body = {
            "collection_name": collection_name,
            "filter": query,
            "object_id": resource_id,
            "organization_id": self.organization_id,
            "plugin_id": self.plugin_id,
            "options": options,
        }

        try:
            response = requests.post(url=self.read_query_api, json=request_body)
        except requests.exceptions.RequestException as exception:
            print(exception)
            return None
        if response.status_code == 200:
            return response.json().get("data")

        return {"status_code": response.status_code, "message": response.reason}

    async def delete(self, collection_name, document_id):
        """
        Function to del data resource from db.

        Args:
            collection_name (str): Name of collection
            Document_ID (str): Resource ID

        Returns:
            None: cannot connect to db
            data: Json object; on success
            data: dict; on api call fails or errors
        """
        body = dict(
            plugin_id=self.plugin_id,
            organization_id=self.organization_id,
            collection_name=collection_name,
            object_id=document_id,
        )
        try:
            response = requests.post(url=self.delete_api, json=body)
        except requests.exceptions.RequestException as exception:
            print(exception)
            return None
        if response.status_code == 200:
            return response.json()

        return {"status_code": response.status_code, "message": response.reason}

    async def get_all_members(self):
        """Gets a list of all members registered in an organisation
        Args:
            org_id (str): The organization's id
        Returns:
            [List]: [list of objects]
        """
        url = self.get_member_api.format(org_id=self.organization_id)
        try:
            response = requests.get(url=url)
        except requests.exceptions.RequestException as exception:
            print(exception)
            return []
        if response.status_code == 200:
            return response.json()["data"]

    async def get_member(self, member_id: str, members: list):
        """Get info of a single registered member in an organisation
        Args:
            org_id (str): The organization's id,
            member_id (str): The member's id
        Returns:
            {dict}: {dict containing user info}
        """
        if members:
            for member in members:
                if member["_id"] == member_id:
                    return member
        return {}


class FileStorage:
    """Serves as a layer for communication of plugin files and server

    Provides a layer of abstraction for communication between plugin
    files and the database on zc_core
    """

    def __init__(
        self, plugin_id: str = PLUGIN_ID, organization_id: str = ORG_ID
    ) -> None:
        self.upload_api = f"{BASE_URL}/upload/file/" + "{pgn_id}"
        self.upload_multiple_api = f"{BASE_URL}/upload/files/" + "{pgn_id}"
        self.delete_file_api = f"{BASE_URL}/delete/file/" + "{pgn_id}"
        self.plugin_id = plugin_id
        self.organization_id = organization_id


DB = DataStorage()  # datastorage class object
fileStore = FileStorage()  # filestorage class object
