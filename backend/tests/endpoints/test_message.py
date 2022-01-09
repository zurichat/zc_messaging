from fastapi_pagination.api import response
import pytest
from fastapi.testclient import TestClient
from main import app

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

    mock_get_user_room.return_value = fake_core_room_data
    mock_write.return_value = write_response
    mock_centrifugo.return_value = centrifugo_response

    result = client.post(send_message_test_url, json=send_message_test_payload)
    assert result.status_code == 201
    success_response["data"]["created_at"] = result.json()["data"]["created_at"]
    assert result.json() == success_response


@pytest.mark.asyncio
async def test_send_message_sender_not_in_room(mock_get_user_room):
    """Send message unsuccessful when sender is not part of the members of the room.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
    """

    mock_get_user_room.return_value = fake_core_room_data
    send_message_test_payload["sender_id"] = "yur859"
    resp = client.post(send_message_test_url, json=send_message_test_payload)
    assert resp.status_code == 404
    assert resp.json() == {"detail": "sender not a member of this room"}


@pytest.mark.asyncio
async def test_send_message_empty_room(mock_get_user_room):
    """Send message unsuccessful when get_rooms returns an empty dictonary.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
    """

    send_message_test_payload["sender_id"] = "e21e10"
    mock_get_user_room.return_value = {}
    res = client.post(send_message_test_url, json=send_message_test_payload)
    assert res.status_code == 404
    assert res.json() == {"detail": "Room not available"}


@pytest.mark.asyncio
async def test_send_message_wrting_to_core_returns_none(mock_get_user_room, mock_write):
    """Send message unsuccessful when writing to zc core return none.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
        mock_write (AsyncMock): Asynchronous external api call
    """

    mock_get_user_room.return_value = fake_core_room_data
    mock_write.return_value = None
    response = client.post(send_message_test_url, json=send_message_test_payload)
    assert response.status_code == 424
    assert response.json() == {"detail": {"Message not sent": None}}


@pytest.mark.asyncio
async def test_send_message_check_status_code(mock_get_user_room, mock_write):
    """Send message unsuccessful when writing to zc core return a response with status_code.

    Args:
        mock_get_room (AsyncMock): Asynchronous external api call
        mock_write (AsyncMock): Asynchronous external api call
    """

    write_response = {"status_code": 422, "message": "unprocessible error"}
    mock_get_user_room.return_value = fake_core_room_data
    mock_write.return_value = write_response
    response = client.post(send_message_test_url, json=send_message_test_payload)
    assert response.status_code == 424
    assert response.json() == {"detail": {"Message not sent": write_response}}


@pytest.mark.asyncio
async def test_update_message_sucessful(
    mock_get_message, mock_update_message, mock_centrifugo
):
    """[summary]

    Args:
        mock_get_message ([type]): [description]
        mock_update_message ([type]): [description]
        mock_centrifugo ([type]): [description]
    """
    mock_get_message.return_value = fake_zc_core_message_data
    mock_update_message.return_value = {
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
async def test_update_message_empty_message(mock_get_message):
    """[summary]

    Args:
        mock_get_message ([type]): [description]
    """
    mock_get_message.return_value = {}
    response = client.put(update_message_test_url, json=update_message_test_payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "Message not found"}


@pytest.mark.asyncio
async def test_update_message_wrong_sender_id(mock_get_message):
    """[summary]

    Args:
        mock_get_message ([type]): [description]
    """
    fake_zc_core_message_data["sender_id"] = "6er34"
    mock_get_message.return_value = fake_zc_core_message_data
    response = client.put(update_message_test_url, json=update_message_test_payload)
    assert response.status_code == 401
    assert response.json() == {
        "detail": "You are not authorized to edit this message"
    }


@pytest.mark.asyncio
async def test_update_message_check_status_code(mock_get_message, mock_update_message):
    """[summary]

    Args:
        mock_get_message ([type]): [description]
        mock_update_message ([type]): [description]
    """
    fake_zc_core_message_data["sender_id"] = "619ba4"
    mock_get_message.return_value = fake_zc_core_message_data
    mock_update_message.return_value = {
        "status_code": 422,
        "message": "unprocessible error",
    }
    response = client.put(update_message_test_url, json=update_message_test_payload)
    assert response.status_code == 424
    assert response.json() == {
        "detail": {"message not edited": mock_update_message.return_value}
    }
