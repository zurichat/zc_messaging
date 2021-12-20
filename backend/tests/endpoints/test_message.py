from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(name="mock_get_user_room")
def fixture_mock_get_user_room(mocker):
    """[summary]

    Args:
        mocker ([type]): [description]

    Returns:
        [type]: [description]
    """
    core_read_mock = AsyncMock()
    mocker.patch("utils.room_utils.DataStorage.read", side_effect=core_read_mock)
    return core_read_mock


@pytest.fixture(name="mock_write")
def fixture_mock_write(mocker):
    """[summary]

    Args:
        mocker ([type]): [description]

    Returns:
        [type]: [description]
    """
    async_mock_write = AsyncMock()
    mocker.patch("endpoints.messages.DataStorage.write", side_effect=async_mock_write)
    return async_mock_write


@pytest.fixture(name="mock_centrifugo")
def fixture_mock_centrifugo(mocker):
    """[summary]

    Args:
        mocker ([type]): [description]

    Returns:
        [type]: [description]
    """
    async_mock_centrifugo = AsyncMock()
    mocker.patch(
        "endpoints.messages.centrifugo_client.publish",
        side_effect=async_mock_centrifugo,
    )
    return async_mock_centrifugo


@pytest.mark.asyncio
async def test_send_message_successful(mock_get_user_room, mock_write, mock_centrifugo):
    """Send message successful

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
        mock_write (AsyncMock): Asynchronous external api call
        mock_centrifugo (AsyncMock): Asynchronous external api call
    """
    success_response = {
        "status": "success",
        "message": "new message sent",
        "data": {
            "room_id": "123456",
            "message_id": "a1a1a1",
            "sender_id": "e21e10",
            "text": "sup bro",
            "files": [],
        },
    }

    fake_core_data = {
        "_id": "619e28c31a5f54782939d59a",
        "created_at": "2021-11-24 11:23:11.361210",
        "created_by": "61696f",
        "description": "Section for general information",
        "id": None,
        "is_archived": False,
        "is_private": False,
        "org_id": "619baf",
        "room_members": {
            "61696f": {"closed": False, "role": "admin", "starred": False},
            "e21e10": {"closed": False, "role": "admin", "starred": False},
        },
        "room_name": "random",
        "room_type": "CHANNEL",
        "topic": "Information",
    }

    write_response = {
        "status": 200,
        "message": "success",
        "data": {"insert_count": 1, "object_id": "a1a1a1"},
    }

    centrifugo_response = {"status_code": 200}

    mock_get_user_room.return_value = fake_core_data
    mock_write.return_value = write_response
    mock_centrifugo.return_value = centrifugo_response
    payload = {
        "text": "sup bro",
    }
    response = client.post(
        "api/v1/org/619ba4/rooms/123456/sender/e21e10/messages", json=payload
    )
    assert response.status_code == 201
    assert response.json() == success_response


@pytest.mark.asyncio
async def test_send_message_unsuccessful_case_1(mock_get_user_room):
    """Send message unsuccessful when sender is not part of the members of the room.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
    """
    fake_core_data = {
        "_id": "619e28c31a5f54782939d59a",
        "created_at": "2021-11-24 11:23:11.361210",
        "created_by": "61696f",
        "description": "Section for general information",
        "id": None,
        "is_archived": False,
        "is_private": False,
        "org_id": "619baf",
        "room_members": {
            "61696f": {"closed": False, "role": "admin", "starred": False},
            "tert435": {"closed": False, "role": "admin", "starred": False},
        },
        "room_name": "random",
        "room_type": "CHANNEL",
        "topic": "Information",
    }

    mock_get_user_room.return_value = fake_core_data
    payload = {
        "text": "sup bro",
    }
    response = client.post(
        "api/v1/org/619ba4/rooms/123456/sender/e21e10/messages", json=payload
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "sender not a member of this room"}


@pytest.mark.asyncio
async def test_send_message_unsuccessful_case_2(mock_get_user_room):
    """Send message unsuccessful when get_rooms returns an empty dictonary.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
    """
    fake_core_data = {}
    mock_get_user_room.return_value = fake_core_data
    payload = {
        "text": "sup bro",
    }
    response = client.post(
        "api/v1/org/619ba4/rooms/123456/sender/e21e10/messages", json=payload
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Room not available"}


@pytest.mark.asyncio
async def test_send_message_unsuccessful_case_3(mock_get_user_room, mock_write):
    """Send message unsuccessful when writing to zc core return none.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
        mock_write (AsyncMock): Asynchronous external api call
    """
    fake_core_data = {
        "_id": "619e28c31a5f54782939d59a",
        "created_at": "2021-11-24 11:23:11.361210",
        "created_by": "61696f",
        "description": "Section for general information",
        "id": None,
        "is_archived": False,
        "is_private": False,
        "org_id": "619baf",
        "room_members": {
            "61696f": {"closed": False, "role": "admin", "starred": False},
            "e21e10": {"closed": False, "role": "admin", "starred": False},
        },
        "room_name": "random",
        "room_type": "CHANNEL",
        "topic": "Information",
    }

    mock_get_user_room.return_value = fake_core_data
    mock_write.return_value = None
    payload = {
        "text": "sup bro",
    }
    response = client.post(
        "api/v1/org/619ba4/rooms/123456/sender/e21e10/messages", json=payload
    )
    assert response.status_code == 424
    assert response.json() == {"detail": {"Message not sent": None}}


@pytest.mark.asyncio
async def test_send_message_unsuccessful_case_4(mock_get_user_room, mock_write):
    """Send message unsuccessful when writing to zc core return a response with status_code.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
        mock_write (AsyncMock): Asynchronous external api call
    """
    fake_core_data = {
        "_id": "619e28c31a5f54782939d59a",
        "created_at": "2021-11-24 11:23:11.361210",
        "created_by": "61696f",
        "description": "Section for general information",
        "id": None,
        "is_archived": False,
        "is_private": False,
        "org_id": "619baf",
        "room_members": {
            "61696f": {"closed": False, "role": "admin", "starred": False},
            "e21e10": {"closed": False, "role": "admin", "starred": False},
        },
        "room_name": "random",
        "room_type": "CHANNEL",
        "topic": "Information",
    }

    write_response = {"status_code": 422, "message": "unprocessible error"}

    mock_get_user_room.return_value = fake_core_data
    mock_write.return_value = write_response
    payload = {
        "text": "sup bro",
    }
    response = client.post(
        "api/v1/org/619ba4/rooms/123456/sender/e21e10/messages", json=payload
    )
    assert response.status_code == 424
    assert response.json() == {"detail": {"Message not sent": write_response}}
