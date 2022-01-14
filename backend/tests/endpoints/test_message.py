# import pytest
# from fastapi.testclient import TestClient
# from main import app

# client = TestClient(app)
# send_message_test_url = "api/v1/org/619ba4/rooms/123456/messages"
# test_payload = {
#     "sender_id": "e21e10",
#     "emojis": [],
#     "richUiData": {
#         "blocks": [
#             {
#                 "key": "eljik",
#                 "text": "HI, I'm mark.. new here",
#                 "type": "unstyled",
#                 "depth": 0,
#                 "inlineStyleRanges": [],
#                 "entityRanges": [],
#                 "data": {},
#             }
#         ],
#         "entityMap": {},
#     },
#     "timestamp": 0,
# }

# fake_core_data = {
#     "_id": "619e28c31a5f54782939d59a",
#     "created_at": "2021-11-24 11:23:11.361210",
#     "created_by": "61696f",
#     "description": "Section for general information",
#     "id": None,
#     "is_archived": False,
#     "is_private": False,
#     "org_id": "619baf",
#     "room_members": {
#         "61696f": {"closed": False, "role": "admin", "starred": False},
#         "e21e10": {"closed": False, "role": "admin", "starred": False},
#     },
#     "room_name": "random",
#     "room_type": "CHANNEL",
#     "topic": "Information",
# }


# @pytest.mark.asyncio
# async def test_send_message_successful(mock_get_user_room, mock_write, mock_centrifugo):
#     """Send message successful

#     Args:
#         mock_get_room (AsyncMock): Asynchronous external api call
#         mock_write (AsyncMock): Asynchronous external api call
#         mock_centrifugo (AsyncMock): Asynchronous external api call
#     """
#     success_response = {
#         "status": "success",
#         "message": "new message sent",
#         "data": {
#             "sender_id": "e21e10",
#             "emojis": [],
#             "richUiData": {
#                 "blocks": [
#                     {
#                         "key": "eljik",
#                         "text": "HI, I'm mark.. new here",
#                         "type": "unstyled",
#                         "depth": 0,
#                         "inlineStyleRanges": [],
#                         "entityRanges": [],
#                         "data": {},
#                     }
#                 ],
#                 "entityMap": {},
#             },
#             "files": [],
#             "saved_by": [],
#             "timestamp": 0,
#             "created_at": "",
#             "room_id": "123456",
#             "org_id": "619ba4",
#             "message_id": "a1a1a1",
#             "edited": False,
#             "threads": [],
#         },
#     }

#     write_response = {
#         "status": 200,
#         "message": "success",
#         "data": {"insert_count": 1, "object_id": "a1a1a1"},
#     }

#     centrifugo_response = {"status_code": 200}

#     mock_get_user_room.return_value = fake_core_data
#     mock_write.return_value = write_response
#     mock_centrifugo.return_value = centrifugo_response

#     response = client.post(send_message_test_url, json=test_payload)
#     assert response.status_code == 201
#     success_response["data"]["created_at"] = response.json()["data"]["created_at"]
#     assert response.json() == success_response


# @pytest.mark.asyncio
# async def test_send_message_sender_not_in_room(mock_get_user_room):
#     """Send message unsuccessful when sender is not part of the members of the room.

#     Args:
#         mock_get_room (AsyncMock): Asynchronous external api call
#     """

#     mock_get_user_room.return_value = fake_core_data
#     test_payload["sender_id"] = "yur859"
#     response = client.post(send_message_test_url, json=test_payload)
#     assert response.status_code == 404
#     assert response.json() == {"detail": "sender not a member of this room"}


# @pytest.mark.asyncio
# async def test_send_message_empty_room(mock_get_user_room):
#     """Send message unsuccessful when get_rooms returns an empty dictonary.

#     Args:
#         mock_get_room (AsyncMock): Asynchronous external api call
#     """

#     test_payload["sender_id"] = "e21e10"
#     mock_get_user_room.return_value = {}
#     response = client.post(send_message_test_url, json=test_payload)
#     assert response.status_code == 404
#     assert response.json() == {"detail": "Room not available"}


# @pytest.mark.asyncio
# async def test_send_message_wrting_to_core_returns_none(mock_get_user_room, mock_write):
#     """Send message unsuccessful when writing to zc core return none.

#     Args:
#         mock_get_room (AsyncMock): Asynchronous external api call
#         mock_write (AsyncMock): Asynchronous external api call
#     """

#     mock_get_user_room.return_value = fake_core_data
#     mock_write.return_value = None
#     response = client.post(send_message_test_url, json=test_payload)
#     assert response.status_code == 424
#     assert response.json() == {"detail": {"Message not sent": None}}


# @pytest.mark.asyncio
# async def test_send_message_check_status_code(mock_get_user_room, mock_write):
#     """Send message unsuccessful when writing to zc core return a response with status_code.

#     Args:
#         mock_get_room (AsyncMock): Asynchronous external api call
#         mock_write (AsyncMock): Asynchronous external api call
#     """

#     write_response = {"status_code": 422, "message": "unprocessible error"}
#     mock_get_user_room.return_value = fake_core_data
#     mock_write.return_value = write_response
#     response = client.post(send_message_test_url, json=test_payload)
#     assert response.status_code == 424
#     assert response.json() == {"detail": {"Message not sent": write_response}}
