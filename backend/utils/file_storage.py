from typing import Any, Union

import requests
from config.settings import settings
from pydantic import AnyHttpUrl


class FileStorage:
    """Serves as a layer for communication of plugin files and server.

    Provides a layer of abstraction for communication between plugin
    files and the database on zc_core.
    """

    def __init__(self, organization_id: str) -> None:
        try:
            response = requests.get(url=f"{settings.BASE_URL}/marketplace/plugins")
            plugins = response.json().get("data").get("plugins")
            plugin = next(
                item for item in plugins if settings.PLUGIN_KEY in item["template_url"]
            )
            self.plugin_id = plugin["id"] if plugin else None
            self.upload_api = f"{settings.BASE_URL}/upload/file/" + self.plugin_id
            self.upload_multiple_api = (
                f"{settings.BASE_URL}/upload/files/" + self.plugin_id
            )
            self.delete_file_api = (
                f"{settings.BASE_URL}/delete/file/" + self.plugin_id
            )
            self.organization_id = organization_id
            self.upload_api_url = f"{settings.BASE_URL}/upload/file/" + self.plugin_id

        except requests.exceptions.RequestException as exception:
            print(exception)

    async def files_upload(
        self, files, token: str
    ) -> Union[dict[str, Any], list[AnyHttpUrl], None]:
        """
        Uploads files to zc_core.

        Args:
            files (list[Any]): A list of files to be uploaded.
            token (str): The user's token.

        Returns:
            On success, a list containing the file urls of the uploaded files.
            _type_: Union[dict[str, Any], list[AnyHttpUrl], None]

            In case of error:

                {
                    "status": 200,
                    "message": "success",
                    "data": null
                }
        """

        # files = [("files", file) for file in files]
        # # NOTE to use when we implement multiple uploads

        headers = {
            "Authorization": "Bearer " + token,
        }

        try:
            response = requests.post(url=self.upload_api, files=files, headers=headers)
        except requests.exceptions.RequestException:
            return None

        if response.status_code == 200:
            return response.json()['data']["file_url"]

        return None
