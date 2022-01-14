import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


get_room_members_url = (
    "api/v1/org/6619ba4671a5f54782939d384//rooms/61dcf855eba8adb50ca13a24/members"
)

fake_data_group_dm = {
    "room_name": "test group dm",
    "room_type": "GROUP_DM",
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
        "619ba4671a5f54782939d385": {
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
    "topic": None,
    "is_private": True,
    "is_archived": False,
    "id": "61dcf855eba8adb50ca13a24",
    "org_id": "619ba4671a5f54782939d384",
    "created_by": "619ba4671a5f54782939d385",
}


@pytest.mark.asyncio
async def test_get_room_members_successful(mock_get_user_room):
    """Tests when room members are retrieved successfully
    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
    """
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
        "619ba4671a5f54782939d385": {
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

    mock_get_user_room.return_value = fake_data_group_dm
    response = client.get(get_room_members_url)
    assert response.status_code == 200
    assert response.json() == read_response


@pytest.mark.asyncio
async def test_get_room_members_room_not_found(mock_get_user_room):
    """Tests when room is not found
    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
    """
    mock_get_user_room.return_value = None
    read_response = {
        "detail": "Room not found",
    }

    response = client.get(get_room_members_url)
    assert response.status_code == 404
    assert response.json() == read_response


@pytest.mark.asyncio
async def test_get_members_reading_from_zc_core_returns_none(mock_get_user_room):
    """Get members reading from zc core returns none.
    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
    """
    mock_get_user_room.return_value = None

    response = client.get(get_room_members_url)
    assert response.status_code == 404
    assert response.json() == {"detail": "Room not found"}


@pytest.mark.asyncio
async def test_get_members_check_status_code(mock_get_user_room, mock_dataStorage_read):
    """Get members unsuccessful when getting from zc core fails.
    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
        mock_dataStorage_read (AsyncMock): Asynchronous external api call
    """
    read_response = {"status_code": 424, "message": "Failed to retrieve room members"}

    mock_get_user_room.return_value = fake_data_group_dm
    mock_dataStorage_read.return_value = read_response

    response = client.get(get_room_members_url)
    assert response.status_code == 404
    assert response.json() == {"detail": "Room not found"}
