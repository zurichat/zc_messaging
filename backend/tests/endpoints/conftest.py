from unittest.mock import AsyncMock

import pytest


@pytest.fixture(name="mock_data_storage_read")
def fixture_mock_data_storage_read(mocker):
    """Patches read data function from ZC Core.

    Args:
       mocker (Mock): An object for patching ZC Core api call.

    Returns:
       AsyncMock: An instance of the AsyncMock class.
    """

    core_read_mock = AsyncMock()
    mocker.patch("utils.db.DataStorage.read", side_effect=core_read_mock)

    return core_read_mock


@pytest.fixture(name="mock_data_storage_write")
def fixture_mock_data_storage_write(mocker):
    """Patches write data function to ZC Core.

    Args:
       mocker (Mock): An object for patching ZC Core api call.

    Returns:
        AsyncMock: An instance of the AsyncMock class.
    """

    async_mock_write = AsyncMock()
    mocker.patch("utils.db.DataStorage.write", side_effect=async_mock_write)

    return async_mock_write


@pytest.fixture(name="mock_centrifugo_publish")
def fixture_mock_centrifugo_publish(mocker):
    """Patches centrifugo external call.

    Args:
        mocker (Mock): An object for patching Centrifugo's publish method call.

    Returns:
        AsyncMock: An instance of the AsyncMock class
    """

    async_mock_centrifugo = AsyncMock()
    mocker.patch(
        "utils.centrifugo.centrifugo_client.publish",
        side_effect=async_mock_centrifugo,
    )

    return async_mock_centrifugo


@pytest.fixture(name="mock_data_storage_update")
def fixture_mock_data_storage_update(mocker):
    """Patches update data function to zc core

    Args:
        mocker (Mock): An object for patching ZC Core api call.

    Returns:
        AsyncMock: An instance of the AsyncMock class
    """

    zc_core_update_data = AsyncMock()
    mocker.patch("utils.db.DataStorage.update", side_effect=zc_core_update_data)

    return zc_core_update_data


@pytest.fixture(name="mock_data_storage_delete")
def fixture_mock_data_storage_delete(mocker):
    """Patches delete data function from zc core.

    Args:
        mocker (Mock): An object for patching ZC Core api call.

    Returns:
        AsyncMock: An instance of the AsyncMock class
    """

    zc_core_update_data = AsyncMock()
    mocker.patch("utils.db.DataStorage.delete", side_effect=zc_core_update_data)

    return zc_core_update_data


@pytest.fixture(name="mock_create_message")
def fixture_mock_create_message(mocker):
    """Patche create_message helper function.

    Args:
       mocker (Mock): An object for patching the create_message function call.

    Returns:
        AsyncMock: An instance of the AsyncMock class
    """

    async_mock_create_message = AsyncMock()
    mocker.patch(
        "utils.message_utils.create_message", side_effect=async_mock_create_message
    )

    return async_mock_create_message
