import requests


PLUGIN_ID = ""
ORG_ID = "61695d8bb2cc8a9af4833d46"


class DataStorage:
    """
    Helper Class as a layer of communication between plugin and db on zc_core
    """

    def __init__(self, request=None):
        self.read_api = (
            "https://api.zuri.chat/data/read/{pgn_id}/{collec_name}/{org_id}?{query}"
        )
        # self.upload_test_api = "http://127.0.0.1:8000/api/v1/testapi/{pgn_id}"
        self.write_api = "https://api.zuri.chat/data/write"
        self.delete_api = "https://api.zuri.chat/data/delete"
        self.upload_api = "https://api.zuri.chat/upload/file/{pgn_id}"
        self.upload_multiple_api = "https://api.zuri.chat/upload/files/{pgn_id}"
        self.delete_file_api = "https://api.zuri.chat/delete/file/{pgn_id}"
        self.read_query_api = "https://api.zuri.chat/data/read"

        if request is None:
            self.plugin_id = PLUGIN_ID
            self.organization_id = ORG_ID
        else:
            self.plugin_id = request.get("PLUGIN_ID", PLUGIN_ID)
            self.organization_id = request.get("ORG_ID")

    async def write(self, collection_name, data):
        """
        Function to write into db

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
        """
        Function to update data from db.
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
        options: dict,
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


DB = DataStorage()
