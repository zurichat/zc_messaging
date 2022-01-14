from unittest import mock
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from main import app
from requests import exceptions
from utils.db import DataStorage

client = TestClient(app)
send_message_test_url = "api/v1/org/619ba4/rooms/123456/messages"
update_message_test_url = "api/v1/org/1234/rooms/343235/messages/346556"
send_message_test_payload = {
    "sender_id": "e21e10",
    "emojis": [],
    "richUiData": {
        "blocks": [
            {
                "key": "eljik",
                "text": "HI, I'm mark.. new here",
                "type": "unstyled",
                "depth": 0,
                "inlineStyleRanges": [],
                "entityRanges": [],
                "data": {},
            }
        ],
        "entityMap": {},
    },
    "timestamp": 0,
}
update_message_test_payload = {
    "richUiData": {
        "blocks": [
            {
                "data": {},
                "depth": 0,
                "entityRanges": [],
                "inlineStyleRanges": [],
                "key": "eljik",
                "text": "HI,  mark",
                "type": "unstyled",
            }
        ],
        "entityMap": {},
    },
    "sender_id": "619ba4",
    "timestamp": 0,
}

fake_core_room_data = {
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


fake_zc_core_message_data = {
    "_id": "346556",
    "created_at": "2021-12-28 19:27:13.620083",
    "edited": False,
    "emojis": [],
    "files": [],
    "org_id": "1234",
    "richUiData": {
        "blocks": [
            {
                "data": {},
                "depth": 0,
                "entityRanges": [],
                "inlineStyleRanges": [],
                "key": "eljik",
                "text": "HI, I'm mark.. new here",
                "type": "unstyled",
            }
        ],
        "entityMap": {},
    },
    "room_id": "343235",
    "saved_by": [],
    "sender_id": "619ba4",
    "threads": [],
    "timestamp": 0,
}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_send_message_successful(
    mock_dataStorage_read, mock_dataStorage_write, mock_centrifugo
):
    """Send message successful

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
        mock_dataStorage_write (AsyncMock): Asynchronous external api call
        mock_centrifugo (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("619ba4")
    db.plugin_id = "34453"
    success_response = {
        "status": "success",
        "message": "new message sent",
        "data": {
            "sender_id": "e21e10",
            "emojis": [],
            "richUiData": {
                "blocks": [
                    {
                        "key": "eljik",
                        "text": "HI, I'm mark.. new here",
                        "type": "unstyled",
                        "depth": 0,
                        "inlineStyleRanges": [],
                        "entityRanges": [],
                        "data": {},
                    }
                ],
                "entityMap": {},
            },
            "files": [],
            "saved_by": [],
            "timestamp": 0,
            "created_at": "",
            "room_id": "123456",
            "org_id": "619ba4",
            "message_id": "a1a1a1",
            "edited": False,
            "threads": [],
        },
    }

    write_response = {
        "status": 200,
        "message": "success",
        "data": {"insert_count": 1, "object_id": "a1a1a1"},
    }

    centrifugo_response = {"status_code": 200}

    mock_dataStorage_read.return_value = fake_core_room_data
    mock_dataStorage_write.return_value = write_response
    mock_centrifugo.return_value = centrifugo_response

    response = client.post(send_message_test_url, json=send_message_test_payload)
    assert response.status_code == 201
    success_response["data"]["created_at"] = response.json()["data"]["created_at"]
    assert response.json() == success_response


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_send_message_sender_not_in_room(mock_dataStorage_read):
    """Send message unsuccessful when sender is not part of the members of the room.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("619ba4")
    db.plugin_id = "34453"
    mock_dataStorage_read.return_value = fake_core_room_data
    send_message_test_payload["sender_id"] = "yur859"
    response = client.post(send_message_test_url, json=send_message_test_payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "sender not a member of this room"}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_send_message_empty_room(mock_dataStorage_read):
    """Send message unsuccessful when get_rooms returns an empty dictonary.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("619ba4")
    db.plugin_id = "34453"
    send_message_test_payload["sender_id"] = "e21e10"
    mock_dataStorage_read.return_value = {}
    response = client.post(send_message_test_url, json=send_message_test_payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "Room not available"}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_send_message_wrting_to_core_returns_none(
    mock_dataStorage_read, mock_dataStorage_write
):
    """Send message unsuccessful when writing to zc core return none.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
        mock_dataStorage_write (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("619ba4")
    db.plugin_id = "34453"
    mock_dataStorage_read.return_value = fake_core_room_data
    mock_dataStorage_write.return_value = None
    response = client.post(send_message_test_url, json=send_message_test_payload)
    assert response.status_code == 424
    assert response.json() == {"detail": {"Message not sent": None}}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_send_message_check_status_code(
    mock_dataStorage_read, mock_dataStorage_write
):
    """Send message unsuccessful when writing to zc core return a response with status_code.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
        mock_dataStorage_write (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("619ba4")
    db.plugin_id = "34453"
    write_response = {"status_code": 422, "message": "unprocessible error"}
    mock_dataStorage_read.return_value = fake_core_room_data
    mock_dataStorage_write.return_value = write_response
    response = client.post(send_message_test_url, json=send_message_test_payload)
    assert response.status_code == 424
    assert response.json() == {"detail": {"Message not sent": write_response}}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_update_message_successful(
    mock_dataStorage_read, mock_dataStorage_update, mock_centrifugo
):
    """Update message successful.

    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
        mock_dataStorage_update (AsyncMock): Asynchronous external api call
        mock_centrifugo (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("619ba4")
    db.plugin_id = "34453"
    mock_dataStorage_read.return_value = fake_zc_core_message_data
    mock_dataStorage_update.return_value = {
        "status": 200,
        "message": "success",
        "data": {"matched_documents": 1, "modified_documents": 1},
    }
    mock_centrifugo.return_value = {"status_code": 200}
    response = client.put(update_message_test_url, json=update_message_test_payload)
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Message edited",
        "data": {
            "_id": "346556",
            "created_at": "2021-12-28 19:27:13.620083",
            "edited": True,
            "emojis": [],
            "files": [],
            "org_id": "1234",
            "richUiData": {
                "blocks": [
                    {
                        "data": {},
                        "depth": 0,
                        "entityRanges": [],
                        "inlineStyleRanges": [],
                        "key": "eljik",
                        "text": "HI,  mark",
                        "type": "unstyled",
                    }
                ],
                "entityMap": {},
            },
            "room_id": "343235",
            "saved_by": [],
            "sender_id": "619ba4",
            "threads": [],
            "timestamp": 0,
        },
    }


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_update_message_empty_message(mock_dataStorage_read):
    """Update message unsuccessful with an invalid message_id.

    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("619ba4")
    db.plugin_id = "34453"
    mock_dataStorage_read.return_value = {}
    response = client.put(update_message_test_url, json=update_message_test_payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "Message not found"}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_update_message_wrong_sender_id(mock_dataStorage_read):
    """Update message unsuccessful with a wrong sender_id provided.

    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("619ba4")
    db.plugin_id = "34453"
    fake_zc_core_message_data["sender_id"] = "6er34"
    mock_dataStorage_read.return_value = fake_zc_core_message_data
    response = client.put(update_message_test_url, json=update_message_test_payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "You are not authorized to edit this message"}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_update_message_check_status_code(
    mock_dataStorage_read, mock_dataStorage_update
):
    """Update message unsuccessful when updating to zc core fails.

    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
        mock_dataStorage_update (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("619ba4")
    db.plugin_id = "34453"
    fake_zc_core_message_data["sender_id"] = "619ba4"
    mock_dataStorage_read.return_value = fake_zc_core_message_data
    mock_dataStorage_update.return_value = {
        "status_code": 422,
        "message": "unprocessible error",
    }
    response = client.put(update_message_test_url, json=update_message_test_payload)
    assert response.status_code == 424
    assert response.json() == {
        "detail": {"message not edited": mock_dataStorage_update.return_value}
    }


@pytest.mark.asyncio
async def test_connection_timeout():
    """Test for connection timeout"""
    with mock.patch.object(
        DataStorage, "__init__", Mock(return_value=exceptions.RequestException)
    ) as mocker:
        DataStorage.__init__("12334")
        mocker.assert_called_with("12334")
