import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


get_room_members_url = "api/v1/org/619ba46/rooms/61dcf85/members"
fake_data_group_dm = {
    "room_name": "test group dm",
    "room_type": "GROUP_DM",
    "room_members": {
        "61696f5": {"role": "admin", "starred": False, "closed": False},
        "6169704": {"role": "admin", "starred": False, "closed": False},
        "619ba46": {"role": "admin", "starred": False, "closed": False},
        "619baa5": {"role": "member", "starred": False, "closed": False},
    },
    "created_at": "2022-01-11 03:18:02.364291",
    "description": None,
    "topic": None,
    "is_private": True,
    "is_archived": False,
    "id": "61dcf85",
    "org_id": "619ba46",
    "created_by": "619ba46",
}


@pytest.mark.asyncio
async def test_get_room_members_successful(mock_get_user_room):
    """Tests when room members are retrieved successfully
    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
    """
    members = {
        "61696f5": {"role": "admin", "starred": False, "closed": False},
        "6169704": {"role": "admin", "starred": False, "closed": False},
        "619ba46": {"role": "admin", "starred": False, "closed": False},
        "619baa5": {"role": "member", "starred": False, "closed": False},
    }
    read_response = {
        "status": "success",
        "message": "Room members retrieved successfully",
        "data": members,
    }

    mock_get_user_room.return_value = fake_data_group_dm
    response = client.get(url=get_room_members_url)
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

    response = client.get(url=get_room_members_url)
    assert response.status_code == 404
    assert response.json() == read_response


@pytest.mark.asyncio
async def test_get_room_members_status_code(mock_get_user_room):
    """Tests when room is not found
    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
    """
    mock_get_user_room.return_value = fake_data_group_dm

    response = client.get(url=get_room_members_url)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_room_members_invalid_url(mock_get_user_room):
    """Tests when room is not found
    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
    """
    fake_url = "api/v1/org/939d384/rooms/0chfy68/members"
    mock_get_user_room.return_value = fake_data_group_dm

    response = client.get(url=get_room_members_url)
    assert get_room_members_url != fake_url
    assert response.status_code == 200
