import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

join_room_test_url = "api/v1/org/619org/rooms/619Chrm1/members/619mem1"
test_join_room_payload = {
    "619mem3": {"role": "member", "starred": False, "closed": False}
}
fake_core_room_data = {
    "_id": "619Chrm1",
    "created_at": "2021-11-24 11:23:11.361210",
    "created_by": "619mem1",
    "description": "Section for general information",
    "id": None,
    "is_archived": False,
    "is_private": False,
    "org_id": "619org",
    "room_members": {
        "619mem1": {"closed": False, "role": "admin", "starred": False},
        "619mem2": {"closed": False, "role": "member", "starred": False},
    },
    "room_name": "random",
    "room_type": "CHANNEL",
    "topic": "Information",
}


@pytest.mark.asyncio
async def test_join_room_success(
    mock_get_user_room, mock_dataStorage_update, mock_centrifugo
):
    """Tests when a member successfully joins a room

    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
        mock_dataStorage_update (AsyncMock): Asynchronous external api call
        mock_centrifugo (AsyncMock): Asynchronous external api call
    """
    success_response = {
        "room_members": {
            "619mem1": {"closed": False, "role": "admin", "starred": False},
            "619mem2": {"closed": False, "role": "member", "starred": False},
            "619mem3": {"closed": False, "role": "member", "starred": False},
        }
    }

    update_response = {
        "status": 200,
        "message": "success",
        "data": {"matched_documents": 1, "modified_documents": 1},
    }

    centrifugo_response = {"status_code": 200}

    mock_get_user_room.return_value = fake_core_room_data
    mock_dataStorage_update.return_value = update_response
    mock_centrifugo.return_value = centrifugo_response

    response = client.put(url=join_room_test_url, json=test_join_room_payload)
    assert response.status_code == 200
    assert response.json() == success_response


@pytest.mark.asyncio
async def test_join_private_room(
    mock_get_user_room, mock_dataStorage_update, mock_centrifugo
):
    """Tests when a member is successfully added to a private room

    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
        mock_dataStorage_update (AsyncMock): Asynchronous external api call
        mock_centrifugo (AsyncMock): Asynchronous external api call
    """
    fake_core_room_data["is_private"] = True
    success_response = {
        "room_members": {
            "619mem1": {"closed": False, "role": "admin", "starred": False},
            "619mem2": {"closed": False, "role": "member", "starred": False},
            "619mem3": {"closed": False, "role": "member", "starred": False},
        }
    }

    update_response = {
        "status": 200,
        "message": "success",
        "data": {"matched_documents": 1, "modified_documents": 1},
    }

    centrifugo_response = {"status_code": 200}

    mock_get_user_room.return_value = fake_core_room_data
    mock_dataStorage_update.return_value = update_response
    mock_centrifugo.return_value = centrifugo_response

    response = client.put(url=join_room_test_url, json=test_join_room_payload)
    assert response.status_code == 200
    assert response.json() == success_response


@pytest.mark.asyncio
async def test_cannot_join_DMroom(mock_get_user_room):
    """Tests when a member is successfully stopped from joining a DM room

    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
    """
    fake_core_room_data["room_type"] = "DM"
    mock_get_user_room.return_value = fake_core_room_data

    response = client.put(url=join_room_test_url, json=test_join_room_payload)
    assert response.status_code == 403
    assert response.json() == {"detail": "DM room cannot be joined"}


@pytest.mark.asyncio
async def test_max_number_for_groupDM(mock_get_user_room):
    """Tests maximum member entries for a group DM

    Args:
        mock_get_user_room (AsyncMock): Asynchronous external api call
    """
    fake_core_room_data["room_type"] = "GROUP_DM"
    mock_get_user_room.return_value = fake_core_room_data
    payload = {
        "619mem3": {"role": "member", "starred": False, "closed": False},
        "619mem4": {"role": "member", "starred": False, "closed": False},
        "619mem5": {"role": "member", "starred": False, "closed": False},
        "619mem6": {"role": "member", "starred": False, "closed": False},
        "619mem7": {"role": "member", "starred": False, "closed": False},
        "619mem8": {"role": "member", "starred": False, "closed": False},
        "619mem9": {"role": "member", "starred": False, "closed": False},
        "619mem10": {"role": "member", "starred": False, "closed": False},
        "619mem11": {"role": "member", "starred": False, "closed": False},
    }
    test_join_room_payload.update(payload)
    response = client.put(url=join_room_test_url, json=test_join_room_payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "the max number for a Group_DM is 9"}
