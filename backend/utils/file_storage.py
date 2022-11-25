import requests
from config.settings import settings


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
            self.upload_api = f"{settings.BASE_URL}/upload/file/" + f"{self.plugin_id}"
            self.upload_multiple_api = (
                f"{settings.BASE_URL}/upload/files/" + f"{self.plugin_id}"
            )
            self.delete_file_api = (
                f"{settings.BASE_URL}/delete/file/" + f"{self.plugin_id}"
            )
            self.organization_id = organization_id

        except requests.exceptions.RequestException as exception:
            print(exception)

    
    def upload(self, file, token):  # takes in files oh, 1 file
        url = self.upload_multiple_api
        files = {"file": file}
        try:
            response = requests.post(
                url=url, files=files, headers={"Authorization": f"{token}"}
            )
        except requests.exceptions.RequestException as e:
            print(e)
            return None
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": response.status_code, "message": response.reason}
