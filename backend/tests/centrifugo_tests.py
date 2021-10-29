import pytest
from fastapi.testclient import TestClient
from main import app
from utils.centrifugo_handler import Events, centrifugo_client

client = TestClient(app)


@pytest.mark.anyio
async def publish_test():
    """
    Performs test to check if centrifugo sends data
    """
    fake_room_id = "1234"
    event = Events.MESSAGE_CREATE
    test_data = {"message": "Hii"}

    response = await centrifugo_client.publish(fake_room_id, event, test_data)
    assert response["status"] == 200
    assert response["event"] == event.value
