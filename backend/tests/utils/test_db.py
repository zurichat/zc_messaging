from unittest import mock
from unittest.mock import Mock

import pytest
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
