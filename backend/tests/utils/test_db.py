from unittest import mock
from unittest.mock import Mock

import pytest
import requests
from config.settings import settings
from requests import exceptions
from utils.db import DataStorage


@pytest.mark.asyncio
async def test_connection_timeout():
    """Test for connection timeout"""
    with mock.patch.object(
        DataStorage, "__init__", Mock(return_value=exceptions.RequestException)
    ) as mocker:
        DataStorage.__init__("12334")
        mocker.assert_called_with("12334")


@pytest.fixture
def TestDB():
    """TestDB fixture"""
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
        yield DataStorage("test")


@pytest.mark.asyncio
class TestDBUpload:
    async def test_upload(self, TestDB: DataStorage):
        """Test upload"""
        files = ["test", "test1"]
        token = "test"

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "status": 200,
                "data": {
                    "files_info": [
                        {
                            "file_url": "test"
                        },
                        {
                            "file_url": "test1"
                        }
                    ]
                }
            }
            response = await TestDB.files_upload(files, token)
            headers = {
                "Authorization": token,
            }
            mock_post.assert_called_once_with(
                url=f"{TestDB.upload_api}/{TestDB.plugin_id}",
                files=[
                    ("files", "test"),
                    ("files", "test1"),
                ],
                headers=headers,
            )
            assert response == ["test", "test1"]

    async def test_upload_error(self, TestDB: DataStorage):
        """Test upload"""
        files = ["test", "test1"]
        token = "test"

        with mock.patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException
            response = await TestDB.files_upload(files, token)
            assert response is None

    async def test_upload_none(self, TestDB: DataStorage):
        """Test upload"""
        files = ["test", "test1"]
        token = "test"

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.json.return_value = {
                "status": 400,
                "data": "test"
            }
            response = await TestDB.files_upload(files, token)
            assert response == {
                "status_code": 400,
                "message": {
                    "status": 400,
                    "data": "test"
                }
            }
