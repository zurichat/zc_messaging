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
            self.upload_api = f"{settings.BASE_URL}/upload/file/" + "{self.plugin_id}"
            self.upload_multiple_api = (
                f"{settings.BASE_URL}/upload/files/" + "{self.plugin_id}"
            )
            self.delete_file_api = (
                f"{settings.BASE_URL}/delete/file/" + "{self.plugin_id}"
            )
            self.organization_id = organization_id

        except requests.exceptions.RequestException as exception:
            print(exception)
