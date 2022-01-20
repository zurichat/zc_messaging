from unittest import mock

import pytest
from fastapi.testclient import TestClient
from main import app
from utils.db import DataStorage

client = TestClient(app)
get_room_members_url = (
    "api/v1/org/3467sd4671a5f5478df56u911/rooms/23dg67l0eba8adb50ca13a24/members"
)
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

fake_org_members = {
    "61696f5ac4133ddaa309dcfe": {"closed": False, "role": "admin", "starred": False},
    "6169704bc4133ddaa309dd07": {"closed": False, "role": "admin", "starred": False},
    "619baa5c1a5f54782939d386": {"closed": False, "role": "member", "starred": False},
}


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_get_room_members_successful(mock_dataStorage_read):
    """Tests when room members are retrieved successfully
    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("3467sd4671a5f5478df56u911")
    db.plugin_id = "34453"

    members = {
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
    }

    read_response = {
        "status": "success",
        "message": "Room members retrieved successfully",
        "data": members,
    }

    mock_dataStorage_read.return_value = fake_room_data

    response = client.get(url=get_room_members_url)
    assert response.status_code == 200
    assert response.json() == read_response


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_get_members_room_not_found(mock_dataStorage_read):
    """Tests when room is not found
    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("3467sd4671a5f5478df56u911")
    db.plugin_id = "34453"

    read_response = {
        "detail": "Room not found",
    }
    mock_dataStorage_read.return_value = None

    response = client.get(url=get_room_members_url)
    assert response.status_code == 404
    assert response.json() == read_response


@pytest.mark.asyncio
@mock.patch.object(DataStorage, "__init__", lambda x, y: None)
async def test_get_members_unsuccessful(mock_dataStorage_read):
    """Get room members unsuccessful

    Args:
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
    """
    db = DataStorage("3467sd4671a5f5478df56u911")
    db.plugin_id = "34453"

    read_response = {"members": {}}
    mock_dataStorage_read.return_value = read_response

    response = client.get(url=get_room_members_url)
    assert response.status_code == 424
    assert response.json() == {"detail": "Failure to retrieve room members"}
