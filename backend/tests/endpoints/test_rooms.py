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

join_room_success_response = {
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

remove_room_member_url_base_url = (
    "api/v1/org/3467sd4671a5f5478df56u911/rooms/23dg67l0eba8adb50ca13a24/members/"
)


class TestJoinRoom:
    """Groups together unit tests related to the `create_room` endpoint."""

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_join_room_success(
        self, mock_data_storage_read, mock_data_storage_update, mock_centrifugo
    ):
        """Tests when a member successfully joins a room.

        Args:
            mock_data_storage_read (AsyncMock): Asynchronous external api call
            mock_data_storage_update (AsyncMock): Asynchronous external api call
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

        mock_data_storage_read.return_value = fake_room_data
        mock_data_storage_update.return_value = update_response
        mock_centrifugo.return_value = centrifugo_response

        response = client.put(url=join_room_test_url, json=join_room_test_payload)
        assert response.status_code == 200
        assert response.json() == join_room_success_response

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_join_room_unsuccessful(
        self, mock_data_storage_read, mock_data_storage_update
    ):
        """Tests for correct error checking when the join room request fails.

        Args:
            mock_data_storage_read (AsyncMock): Asynchronous external api call
            mock_data_storage_update (AsyncMock): Asynchronous external api call
        """
        db = DataStorage("3467sd4671a5f5478df56u911")
        db.plugin_id = "34453"

        mock_data_storage_read.return_value = fake_room_data
        mock_data_storage_update.return_value = None
        response = client.put(url=join_room_test_url, json={})

        assert response.status_code == 424
        assert response.json() == {"detail": "failed to add new members to room"}

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_room_not_found(
        self, mock_data_storage_read, mock_data_storage_update
    ):
        """Tests for correct error checking when room is not found.

        Args:
            mock_data_storage_read (AsyncMock): Asynchronous external api call
            mock_data_storage_update (AsyncMock): Asynchronous external api call
        """
        db = DataStorage("3467sd4671a5f5478df56u911")
        db.plugin_id = "34453"

        mock_data_storage_read.return_value = {}
        mock_data_storage_update.return_value = None
        response = client.put(url=join_room_test_url, json=join_room_test_payload)

        assert response.status_code == 403
        assert response.json() == {"detail": "room not found"}

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_add_to_private_room_by_admin(
        self, mock_data_storage_read, mock_data_storage_update, mock_centrifugo
    ):
        """Tests when a member is successfully added to a private room.

        Args:
            mock_data_storage_read (AsyncMock): Asynchronous external api call
            mock_data_storage_update (AsyncMock): Asynchronous external api call
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
        mock_data_storage_read.return_value = fake_room_data
        mock_data_storage_update.return_value = update_response
        mock_centrifugo.return_value = centrifugo_response

        response = client.put(
            url=join_room_test_url.replace(
                "619baa5939d386c1a5f54782", "61696f5ac4133ddaa309dcfe"
            ),
            json=join_room_test_payload,
        )
        assert response.status_code == 200
        assert response.json() == join_room_success_response

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_add_to_private_room_by_non_admin(self, mock_data_storage_read):
        """Tests for correct error checking when a non-admin tries to add a member to a private room.

        Args:
            mock_data_storage_read (AsyncMock): Asynchronous external api call
        """
        db = DataStorage("3467sd4671a5f5478df56u911")
        db.plugin_id = "34453"

        fake_room_data["is_private"] = True
        mock_data_storage_read.return_value = fake_room_data

        response = client.put(url=join_room_test_url, json=join_room_test_payload)
        assert response.status_code == 401
        assert response.json() == {"detail": "only admins can add new members"}

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_cannot_join_dm_room(self, mock_data_storage_read):
        """Tests when a member is successfully stopped from joining a DM room.

        Args:
            mock_data_storage_read (AsyncMock): Asynchronous external api call
        """
        db = DataStorage("3467sd4671a5f5478df56u911")
        db.plugin_id = "34453"

        fake_room_data["room_type"] = "DM"
        mock_data_storage_read.return_value = fake_room_data

        response = client.put(url=join_room_test_url, json=join_room_test_payload)
        assert response.status_code == 403
        assert response.json() == {"detail": "DM room cannot be joined"}

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_max_number_for_group_dm(self, mock_data_storage_read):
        """Tests maximum member entries for a group DM.

        Args:
            mock_data_storage_read (AsyncMock): Asynchronous external api call
        """
        db = DataStorage("3467sd4671a5f5478df56u911")
        db.plugin_id = "34453"

        fake_room_data["room_type"] = "GROUP_DM"
        mock_data_storage_read.return_value = fake_room_data

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


class TestGetRoomMembers:
    """Groups together unit tests related to the `get_members` endpoint."""

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_get_room_members_successful(self, mock_data_storage_read):
        """Tests when room members are retrieved successfully.
        Args:
            mock_data_storage_read (AsyncMock): Asynchronous external api call
        """
        db = DataStorage("3467sd4671a5f5478df56u911")
        db.plugin_id = "34453"

        members = fake_room_data["room_members"]
        success_response = {
            "status": "success",
            "message": "Room members retrieved successfully",
            "data": members,
        }

        mock_data_storage_read.return_value = fake_room_data

        response = client.get(url=get_room_members_url)
        assert response.status_code == 200
        assert response.json() == success_response

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_get_members_room_not_found(self, mock_data_storage_read):
        """Tests when room is not found.
        Args:
            mock_data_storage_read (AsyncMock): Asynchronous external api call
        """
        db = DataStorage("3467sd4671a5f5478df56u911")
        db.plugin_id = "34453"

        read_response = None
        mock_data_storage_read.return_value = read_response

        response = client.get(url=get_room_members_url)
        assert response.status_code == 404
        assert response.json() == {"detail": "Room not found"}

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_get_members_unsuccessful(self, mock_data_storage_read):
        """Test when getting room members fails.

        Args:
            mock_data_storage_read (AsyncMock): Asynchronous external api call
        """
        db = DataStorage("3467sd4671a5f5478df56u911")
        db.plugin_id = "34453"

        read_response = {"members": {}}
        mock_data_storage_read.return_value = read_response

        response = client.get(url=get_room_members_url)
        assert response.status_code == 424
        assert response.json() == {"detail": "Failure to retrieve room members"}


class TestRemoveRoomMember:
    """Groups together unit tests related to the `remove_member` endpoint."""

    @pytest.mark.parametrize(
        "url, status_code, json_response",
        [
            (
                f"{remove_room_member_url_base_url}619baa5c1a5f54782939d386",
                200,
                {
                    "status": "success",
                    "message": "user removed from room successfully",
                    "data": {
                        "member_id": "619baa5c1a5f54782939d386",
                        "room_id": "23dg67l0eba8adb50ca13a24",
                    },
                },
            ),
            (
                f"{remove_room_member_url_base_url}61696f5ac4133ddaa309dcfe"
                + "?admin_id=6169704bc4133ddaa309dd07",
                200,
                {
                    "status": "success",
                    "message": "user removed from room successfully",
                    "data": {
                        "member_id": "61696f5ac4133ddaa309dcfe",
                        "room_id": "23dg67l0eba8adb50ca13a24",
                    },
                },
            ),
            (
                f"{remove_room_member_url_base_url}1696f5ac4133ddaa309dcfe"
                + "?admin_id=6169704bc4133ddaa309dd07",
                404,
                {"detail": "user not a member of the room"},
            ),
            (
                f"{remove_room_member_url_base_url}1696f5ac4133ddaa309dcfe",
                404,
                {"detail": "user not a member of the room"},
            ),
            (
                f"{remove_room_member_url_base_url}61696f5ac4133ddaa309dcfe"
                + "?admin_id=6169704bc4133ddaa309dd90",
                404,
                {"detail": "admin id specified not a member of the room"},
            ),
            (
                f"{remove_room_member_url_base_url}61696f5ac4133ddaa309dcfe"
                + "?admin_id=619baa5c1a5f54782939d386",
                403,
                {"detail": "must be an admin to remove member"},
            ),
            (
                f"{remove_room_member_url_base_url}619ba4671a5f54782939d385",
                403,
                {
                    "detail": "channel owner cannot leave channel, archive channel or make another member owner"
                },
            ),
            (
                f"{remove_room_member_url_base_url}619ba4671a5f54782939d385?"
                + "admin_id=6169704bc4133ddaa309dd07",
                403,
                {
                    "detail": "channel owner cannot leave channel, archive channel or make another member owner"
                },
            ),
            (
                f"{remove_room_member_url_base_url}6169704bc4133ddaa309dd07?"
                + "admin_id=6169704bc4133ddaa309dd07",
                403,
                {"detail": "cannot remove yourself"},
            ),
        ],
    )
    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_remove_room_member(self, init_mocks, url, status_code, json_response):
        """
        Test 1: Leave room successfully.
        Test 2: Remove member successfully.
        Test 3: A non member cannot leave a room.
        Test 4: Cannot remove a non member.
        Test 5: A non member cannot remove anyone from the room.
        Test 6: A non admin cannot remove anyone.
        Test 7: Room owner cannot leave room.
        Test 8: Room owner cannot be removed.
        Test 9: A member cannot remove itself, must be removed by an admin or leave.

        Args:
            init_mocks (Tuple): Tuple containing Fake room data and Asynchronous external api calls
            url (str): test url
            status_code (int): expected response code
            json_response (Dict): expected json response
        """

        init_fake_room, mock_data_storage_read, mock_data_storage_update = init_mocks

        db = DataStorage("3467sd4671a5f5478df56u911")
        db.plugin_id = "34453"

        update_response = {
            "status": 200,
            "message": "success",
            "data": {"matched_documents": 1, "modified_documents": 1},
        }

        mock_data_storage_read.return_value = init_fake_room
        mock_data_storage_update.return_value = update_response

        response = client.patch(url=url)

        assert response.status_code == status_code
        assert response.json() == json_response

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_remove_room_member_wrong_room_id(self, mock_data_storage_read):
        """
        Cannot leave a non-existent room

        Args:
            mock_datastorage_read (AyncMock): Asynchronous external api call
        """

        db = DataStorage("3467sd4671a5f5478df56u911")
        db.plugin_id = "34453"

        mock_data_storage_read.return_value = {}

        response = client.patch(
            url=f"{remove_room_member_url_base_url}61696f5ac4133ddaa309dcfe"
            + "?admin_id=6169704bc4133ddaa309dd07",
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "room does not exist"}

    @pytest.mark.asyncio
    @mock.patch.object(DataStorage, "__init__", lambda x, y: None)
    async def test_remove_room_member_from_dm(self, init_fake_room, mock_data_storage_read):
        """
        Member cannot leave a DM room

        Args:
            mock_datastorage_read (AyncMock): Asynchronous external api call
        """

        db = DataStorage("3467sd4671a5f5478df56u911")
        db.plugin_id = "34453"

        init_fake_room["room_type"] = "DM"

        mock_data_storage_read.return_value = init_fake_room

        response = client.patch(
            url=f"{remove_room_member_url_base_url}61696f5ac4133ddaa309dcfe"
            + "?admin_id=6169704bc4133ddaa309dd07",
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "cannot remove member from DM rooms"}
