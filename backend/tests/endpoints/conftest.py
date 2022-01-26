from unittest.mock import AsyncMock

import pytest


@pytest.fixture(name="mock_dataStorage_read")
def fixture_mock_dataStorage_read(mocker):
    """Patch for reading data from zc core.

    Args:
       mocker (Mock): For patching a third-party api call

    Returns:
       AsyncMock: An instance of the asyncmock class
    """
    core_read_mock = AsyncMock()
    mocker.patch("utils.db.DataStorage.read", side_effect=core_read_mock)
    return core_read_mock


@pytest.fixture(name="mock_dataStorage_write")
def fixture_mock_dataStorage_write(mocker):
    """Patch for writing to zc core.

    Args:
       mocker (Mock): For patching a third-party api call

    Returns:
        AsyncMock: An instance of the asyncmock class
    """
    async_mock_write = AsyncMock()
    mocker.patch("utils.db.DataStorage.write", side_effect=async_mock_write)
    return async_mock_write


@pytest.fixture(name="mock_centrifugo")
def fixture_mock_centrifugo(mocker):
    """Patch for centrifugo external api call

    Args:
        mocker (Mock): For patching a third-party api call

    Returns:
        AsyncMock: An instance of the asyncmock class
    """
    async_mock_centrifugo = AsyncMock()
    mocker.patch(
        "utils.centrifugo.centrifugo_client.publish",
        side_effect=async_mock_centrifugo,
    )
    return async_mock_centrifugo


@pytest.fixture(name="mock_dataStorage_update")
def fixture_mock_dataStorage_update(mocker):
    """Patch for updating a document to zc core

    Args:
        mocker (Mock): For patching a third-party api call

    Returns:
        AsyncMock: An instance of the asyncmock class
    """
    zc_core_update_data = AsyncMock()
    mocker.patch("utils.db.DataStorage.update", side_effect=zc_core_update_data)
    return zc_core_update_data


@pytest.fixture(name="mock_dataStorage_delete")
def fixture_mock_dataStorage_delete(mocker):
    """Patch for deleting a document to zc core

    Args:
        mocker (Mock): For patching a third-party api call

    Returns:
        AsyncMock: An instance of the asyncmock class
    """
    zc_core_update_data = AsyncMock()
    mocker.patch("utils.db.DataStorage.delete", side_effect=zc_core_update_data)
    return zc_core_update_data


@pytest.fixture(name="mock_get_room_members")
def fixture_mock_get_room_members(mocker):
    """Patch for getting room members.

    Args:
       mocker (Mock): For patching a third-party api call

    Returns:
       AsyncMock: An instance of the asyncmock class
    """
    mock_get_room_members = AsyncMock()
    mocker.patch("utils.room_utils.DataStorage.read", side_effect=mock_get_room_members)
    return mock_get_room_members
