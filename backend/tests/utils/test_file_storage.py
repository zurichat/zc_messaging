from unittest import mock
from unittest.mock import Mock

import pytest
from config.settings import settings
from requests.exceptions import RequestException
from utils.file_storage import FileStorage


@pytest.fixture
def DummyFileStorage():
    """TestFileStorage fixture"""
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = Mock()
        mock_get.return_value.json.return_value = {
            "data": {
                "plugins": [
                    {
                        "template_url": settings.PLUGIN_KEY,
                        "id": "test",
                    }
                ]
            }
        }
        yield FileStorage("test")


@pytest.mark.asyncio
class TestFileStorageUpload:
    async def test_init(self, DummyFileStorage: FileStorage):
        """Test init"""
        assert DummyFileStorage.plugin_id == "test"
        assert DummyFileStorage.upload_api == \
            f"{settings.BASE_URL}/upload/file/test"
        assert DummyFileStorage.upload_multiple_api == \
            f"{settings.BASE_URL}/upload/files/test"

    async def test_success(self, DummyFileStorage: FileStorage):
        """Test upload"""
        files = [b"", b""]
        token = "test"

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "status": 200,
                "data": {
                    "files_info": [
                        {
                            "file_url": "test",
                            "original_name": "test"
                        },
                        {
                            "file_url": "test1",
                            "original_name": "test1"
                        }
                    ]
                }
            }
            response = await DummyFileStorage.files_upload(files, token)
            headers = {
                "Authorization": "Bearer " + token,
            }
            mock_post.assert_called_once_with(
                url=DummyFileStorage.upload_multiple_api,
                files=[
                    ("file", b""),
                    ("file", b""),
                ],
                headers=headers,
            )
            assert response == [
                {
                    "file_url": "test",
                    "original_name": "test"
                },
                {
                    "file_url": "test1",
                    "original_name": "test1"
                }
            ]

    async def test_storage_failure(self, DummyFileStorage: FileStorage):
        """Test upload"""
        files = [b"", b""]
        token = "test"

        with mock.patch('requests.post') as mock_post:
            mock_post.side_effect = RequestException
            response = await DummyFileStorage.files_upload(files, token)
            assert response is None

    async def test_upload_error(self, DummyFileStorage: FileStorage):
        """Test upload"""
        files = [b"", b""]
        token = "test"

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.json.return_value = {
                "status": 400,
                "message": "error message"
            }
            response = await DummyFileStorage.files_upload(files, token)
            assert response == "error message"
