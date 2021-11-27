import pytest
from utils.centrifugo import Events, centrifugo_client


@pytest.mark.anyio
async def test_publish():
    """
    tests for centrifugo publish data
    """
    fake_room_id = "1234"
    event = Events.MESSAGE_CREATE
    test_data = {"message": "Hii"}

    response = await centrifugo_client.publish(fake_room_id, event, test_data)
    assert response["status"] == 200
    assert response["event"] == event.value
    assert response["data"] != {}


@pytest.mark.anyio
async def test_unsubscribe():
    """
    tests for centrifugo unsubscribe
    """
    fake_user = "3214231223"
    fake_room_id = "123121313"

    response = await centrifugo_client.unsubscribe(fake_user, fake_room_id)
    assert response["status"] == 200
    assert response["event"] == "unsubscribe"
    assert response["data"]["user"] == fake_user
    assert response["data"]["room"] == fake_room_id
