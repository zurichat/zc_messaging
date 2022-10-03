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


@pytest.fixture(name="mock_centrifugo")
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


@pytest.fixture(name="init_fake_room")
def fixture_initialize_fake_room_data():
    """A fixture that initialises a new fake room data for each test

    Returns:
        Dict: An room dictionary
    """
    return {
        "room_name": "General",
        "room_type": "CHANNEL",
        "room_members": {
            "61696f5ac4133ddaa309dcfe": {
                "closed": False,
                "role": "admin",
                "starred": False,
            },
            "6169704bc4133ddaa309dd07": {
                "closed": False,
                "role": "admin",
                "starred": False,
            },
            "619baa5c1a5f54782939d386": {
                "closed": False,
                "role": "member",
                "starred": False,
            },
            "619ba4671a5f54782939d385": {
                "closed": False,
                "role": "admin",
                "starred": True,
            },
            "619ba4671a5f54785939d385": {
                "closed": False,
                "role": "member",
                "starred": True,
            },
        },
        "created_at": "2022-01-11 03:18:02.364291",
        "description": None,
        "topic": "General Information",
        "is_private": False,
        "is_archived": False,
        "_id": "23dg67l0eba8adb50ca13a24",
        "org_id": "3467sd4671a5f5478df56u911",
        "created_by": "619ba4671a5f54782939d385",
    }


@pytest.fixture(name="init_mocks")
def fixture_initialize_mocks(
    init_fake_room,
    mock_data_storage_read,
    mock_data_storage_update,
):
    """A fixture that initialises a necessary mocks;
       fake_room data, dataStorage_read and dataStorage_update

    Returns:
        Tuple: An tuple of dict, AsyncMock, AsyncMock
    """
    return (init_fake_room, mock_data_storage_read, mock_data_storage_update)

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
