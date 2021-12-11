from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

fake_room_id = "44523d5325dsdf"
fake_org_id = "1223209805sdfsa902"
fake_message_data = {
        "sender_id": "425324132312",
        "room_id": fake_room_id,
        "text": "does it work well?",
        "reactions": [],
        "files": [],
        "saved_by": [],
        "is_pinned": False,
        "is_edited": False,
        "created_at": "2021-12-11 01:44:37.582879",
        "threads": []
        }

def test_send_message():
    """ test for the send message endpoint"""

    fake_response_output = {
        "message_id": "33090940900",
        "message_data": fake_message_data
    }

    response = client.post(
        "/org/{org_id}/rooms/{room_id}/messages",
        json= fake_message_data
        )
    assert response.status_code == 201
    assert response.json() == fake_response_output

def test_message_not_sent():
    """test response when message is not sent successfully"""

    response = client.post(
        "/org/{fake_org_id}/rooms/{fake_room_id}/messages",
        json= fake_message_data
        )
    
    assert response.status_code == 424
    assert response.json() == {"detail": {"message not sent": {}}}

