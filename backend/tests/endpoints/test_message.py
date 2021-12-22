from fastapi.testclient import TestClient
from main import app
from utils.db import DataStorage

client = TestClient(app)


fake_room_id = "44523d5325dsdf"
fake_org_id = "1223209805sdfsa902"
fake_org_id = ("42893209343920",)
fake_sender_id = "425324132312"
fake_message_obj = {
    "sender_id": fake_sender_id,
    "room_id": fake_room_id,
    "org_id": fake_org_id,
    "message_id": "34o003409",
    "text": "does it work well?",
    "reactions": [],
    "files": [],
    "saved_by": [],
    "is_pinned": False,
    "is_edited": False,
    "created_at": "2021-12-11 01:44:37.582879",
    "threads": [],
}
DB = DataStorage(fake_org_id)


def test_send_message(monkeypatch):
    """test for the send message endpoint"""

    def mock_post():
        return {"status": 201, "message": {"_id": "34928349287395289"}}

    monkeypatch.setattr(DB, "write", mock_post)

    fake_response_output = {
        "room_id": fake_room_id,
        "message_id": "61696f43c4133ddga309dcf6",
        "text": "str",
        "files": "HTTP url(s)",
        "sender_id": fake_sender_id,
    }
    response = client.post(
        "/org/{org_id}/rooms/{room_id}/sender/{sender_id}/messages",
        json=fake_message_obj,
    )
    assert response.status_code == 201
    assert response.json() == fake_response_output


def test_message_not_sent(monkeypatch):
    """test response when message is not sent successfully"""

    def mock_post():
        return {
            "detail": {
                "Message not sent": {
                    "status_code": 200,
                    "message": {
                        "status": 406,
                        "message": "maximum collections limit reached",
                    },
                }
            }
        }

    monkeypatch.setattr(DB, "write", mock_post)

    response = client.post(
        "/org/{org_id}/rooms/{room_id}/sender/{sender_id}/messages",
        json=fake_message_obj,
    )

    assert response.status_code == 424
    assert response.json() == {"detail": {"message not sent": {}}}
