import pytest

from utils.message_utils import upload_file
from unittest import mock
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_upload_file():
    """Test upload file"""

    class MockDataStorage:
        async def upload(self, files, token):
            print("called")
            return ['test', 'test1']

    with mock.patch(
        'utils.message_utils.DataStorage',
        return_value=MockDataStorage()
    ):
        files = ["test", "test1"]
        token = "test"
        response = await upload_file("test", files, token)
        assert response == ['test', 'test1']


@pytest.mark.asyncio
async def test_upload_file_http_exception():
    """Test upload file"""

    class MockDataStorage:
        async def upload(self, files, token):
            return None

    with mock.patch(
        'utils.message_utils.DataStorage',
        return_value=MockDataStorage()
    ):
        with pytest.raises(HTTPException):
            files = ["test", "test1"]
            token = "test"
            await upload_file("test", files, token)

    class MockDataStorage:
        async def upload(self, files, token):
            return {
                "status_code": 400,
                "message": {
                    "data": "test"
                }
            }

    with mock.patch(
        'utils.message_utils.DataStorage',
        return_value=MockDataStorage()
    ):
        with pytest.raises(HTTPException):
            files = ["test", "test1"]
            token = "test"
            await upload_file("test", files, token)









