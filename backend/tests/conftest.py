from unittest.mock import AsyncMock

import pytest


@pytest.fixture(name="mock_get_user_room")
def fixture_mock_get_user_room(mocker):
    """Patch for reading zc core.

    Args:
       mocker (Mock): For patching a third-party api call

    Returns:
       AsyncMock: An instance of the asyncmock class
    """
    core_read_mock = AsyncMock()
    mocker.patch("endpoints.rooms.DataStorage.read", side_effect=core_read_mock)
    return core_read_mock


@pytest.fixture(name="mock_write")
def fixture_mock_write(mocker):
    """Patch for writing to zc core.

    Args:
       mocker (Mock): For patching a third-party api call

    Returns:
        AsyncMock: An instance of the asyncmock class
    """
    async_mock_write = AsyncMock()
    mocker.patch("endpoints.messages.DataStorage.write", side_effect=async_mock_write)
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
        "endpoints.messages.centrifugo_client.publish",
        side_effect=async_mock_centrifugo,
    )
    return async_mock_centrifugo


@pytest.fixture(name="mock_get_message")
def fixture_mock_get_message(mocker):
    """[summary]

    Args:
        mocker ([type]): [description]

    Returns:
        [type]: [description]
    """
    zc_core_read_data = AsyncMock()
    mocker.patch("endpoints.messages.DataStorage.read", side_effect=zc_core_read_data)
    return zc_core_read_data


@pytest.fixture(name="mock_update_message")
def fixture_mock_update_message(mocker):
    """[summary]

    Args:
        mocker ([type]): [description]

    Returns:
        [type]: [description]
    """
    zc_core_update_data = AsyncMock()
    mocker.patch(
        "endpoints.messages.DataStorage.update", side_effect=zc_core_update_data
    )
    return zc_core_update_data
