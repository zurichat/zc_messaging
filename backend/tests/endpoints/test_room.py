from unittest import mock

import pytest
from fastapi.testclient import TestClient
from main import app
from utils.db import DataStorage

client = TestClient(app)

join_room_test_url = (
    "api/v1/org/3467sd4671a5f5478df56u911/rooms/23dg67l0eba8adb50ca13a24/"
    + "members/619baa5939d386c1a5f54782"
)

join_room_test_payload = {
    "619baa5939d386c1a5f54782": {
        "closed": False,
        "role": "member",
        "starred": False,
    }
}

fake_room_data = {
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
    },
    "created_at": "2022-01-11 03:18:02.364291",
    "description": None,
    "topic": "General Information",
    "is_private": False,
    "is_archived": False,
    "id": "23dg67l0eba8adb50ca13a24",
    "org_id": "3467sd4671a5f5478df56u911",
    "created_by": "619ba4671a5f54782939d385",
}

success_response = {
    "status": "success",
    "message": "member(s) successfully added",
    "data": {
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
            "619baa5939d386c1a5f54782": {
                "closed": False,
                "role": "member",
                "starred": False,
            },
        }
    },
}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_join_room_success(
    mock_dataStorage_read, mock_dataStorage_update, mock_centrifugo
):
    """Tests when a member successfully joins a room

    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
        mock_dataStorage_update (AsyncMock): Asynchronous external api call
        mock_centrifugo (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("3467sd4671a5f5478df56u911")
    db.plugin_id = "34453"

    update_response = {
        "status": 200,
        "message": "success",
        "data": {"matched_documents": 1, "modified_documents": 1},
    }

    centrifugo_response = {"status_code": 200}

    mock_dataStorage_read.return_value = fake_room_data
    mock_dataStorage_update.return_value = update_response
    mock_centrifugo.return_value = centrifugo_response

    response = client.put(url=join_room_test_url, json=join_room_test_payload)
    assert response.status_code == 200
    assert response.json() == success_response


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_join_room_unsuccessful(mock_dataStorage_read, mock_dataStorage_update):
    """Tests when a member successfully joins a room

    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
        mock_dataStorage_update (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("3467sd4671a5f5478df56u911")
    db.plugin_id = "34453"

    mock_dataStorage_read.return_value = fake_room_data
    mock_dataStorage_update.return_value = None
    response = client.put(url=join_room_test_url, json={})

    assert response.status_code == 424
    assert response.json() == {"detail": "failed to add new members to room"}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_add_to_private_room_by_admin(
    mock_dataStorage_read, mock_dataStorage_update, mock_centrifugo
):
    """Tests when a member is successfully added to a private room

    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
        mock_dataStorage_update (AsyncMock): Asynchronous external api call
        mock_centrifugo (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("3467sd4671a5f5478df56u911")
    db.plugin_id = "34453"

    update_response = {
        "status": 200,
        "message": "success",
        "data": {"matched_documents": 1, "modified_documents": 1},
    }

    centrifugo_response = {"status_code": 200}

    fake_room_data["is_private"] = True
    mock_dataStorage_read.return_value = fake_room_data
    mock_dataStorage_update.return_value = update_response
    mock_centrifugo.return_value = centrifugo_response

    response = client.put(
        url=join_room_test_url.replace(
            "619baa5939d386c1a5f54782", "61696f5ac4133ddaa309dcfe"
        ),
        json=join_room_test_payload,
    )
    assert response.status_code == 200
    assert response.json() == success_response


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_add_to_private_room_by_non_admin(mock_dataStorage_read):
    """Tests when a member is successfully added to a private room

    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
        mock_dataStorage_update (AsyncMock): Asynchronous external api call
        mock_centrifugo (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("3467sd4671a5f5478df56u911")
    db.plugin_id = "34453"

    fake_room_data["is_private"] = True
    mock_dataStorage_read.return_value = fake_room_data

    response = client.put(url=join_room_test_url, json=join_room_test_payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "only admins can add new members"}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_cannot_join_DMroom(mock_dataStorage_read):
    """Tests when a member is successfully stopped from joining a DM room

    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("3467sd4671a5f5478df56u911")
    db.plugin_id = "34453"

    fake_room_data["room_type"] = "DM"
    mock_dataStorage_read.return_value = fake_room_data

    response = client.put(url=join_room_test_url, json=join_room_test_payload)
    assert response.status_code == 403
    assert response.json() == {"detail": "DM room cannot be joined"}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_max_number_for_groupDM(mock_dataStorage_read):
    """Tests maximum member entries for a group DM

    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("3467sd4671a5f5478df56u911")
    db.plugin_id = "34453"

    fake_room_data["room_type"] = "GROUP_DM"
    mock_dataStorage_read.return_value = fake_room_data

    payload = {
        "619baa5c1a39d3865f547829": {
            "closed": False,
            "role": "member",
            "starred": False,
        },
        "619ba1a5f54782a5939d386c": {
            "closed": False,
            "role": "member",
            "starred": False,
        },
        "619baa39d35c1a5f54782986": {
            "closed": False,
            "role": "member",
            "starred": False,
        },
        "619bc1a5f5aa5939d3864782": {
            "closed": False,
            "role": "member",
            "starred": False,
        },
        "619baa5782939d38c1a5f546": {
            "closed": False,
            "role": "member",
            "starred": False,
        },
        "619baaa5f54785939d386c12": {
            "closed": False,
            "role": "member",
            "starred": False,
        },
        "6194782939d38baa5c1a5f56": {
            "closed": False,
            "role": "member",
            "starred": False,
        },
    }
    join_room_test_payload.update(payload)

    response = client.put(url=join_room_test_url, json=join_room_test_payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "the max number for a Group_DM is 9"}
