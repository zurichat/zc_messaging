import asyncio
import concurrent.futures
from datetime import datetime
from typing import Any, Dict, List

from fastapi import HTTPException, status
from pydantic import AnyHttpUrl, BaseModel, Field, root_validator
from utils.room_utils import get_room


class Emoji(BaseModel):
    """
    Provides the nested object for reactions to message
    """
    name: str
    count: int
    emoji: str
    reactedUsersId: List[str] = []


# class RichUiDataBlock(BaseModel):
#     """
#     """
#     key: str
#     text: str
#     type: str
#     depth: int
#     inlineStyleRanges: List[RichUiStyleRange] = []
#     entityRanges: List[RichUiEntityRange] = []
#     data: Any


# class RichUiEntityData(BaseModel):
#     """
#     """
#     mention: RichUiEntityDataMention
#     emojiUnicode: str



# class RichUiEntity(BaseModel):
#     """
#     """
#     type: str
#     mutability: str
#     data: RichUiEntityData


# class RichUiData(BaseModel):
#     """
#     Mirrors the RichUiData model from the rich text library.
#     """
#     blocks: List[RichUiDataBlock] = []
#     entityMap: Dict[str, RichUiEntity] = {}


class MessageRequest(BaseModel):
    """
    Provides a base model for all threads
    """

    text: str
    sender_id: str
    emojis: List[Emoji] = []
    richUiData: Any
    files: List[AnyHttpUrl] = []
    saved_by: List[str] = []
    created_at: str = str(datetime.utcnow())

"""
{
    "message_id": "1640179225324",
    "sender_id": "619ba4671a5f54782939d385",
    "timestamp": 1640179225324,
    "emojis": [],
    "richUiData": {
        "blocks": [
            {
                "key": "eljik",
                "text": "HI, I'm mark.. new here",
                "type": "unstyled",
                "depth": 0,
                "inlineStyleRanges": [],
                "entityRanges": [],
                "data": {}
            }
        ],
        "entityMap": {}
    }
}
{
    "message_id": "1640204440922",
    "sender_id": "619ba4671a5f54782939d385",
    "timestamp": 1640204440922,
    "emojis": [],
    "richUiData": {
        "blocks": [
            {
                "key": "f3s6p",
                "text": "@funkymikky4ril hello :face_with_raised_eyebrow: ",
                "type": "unstyled",
                "depth": 0,
                "inlineStyleRanges": [],
                "entityRanges": [
                    {
                        "offset": 0,
                        "length": 15,
                        "key": 0
                    },
                    {
                        "offset": 22,
                        "length": 1,
                        "key": 1
                    }
                ],
                "data": {}
            }
        ],
        "entityMap": {
            "0": {
                "type": "mention",
                "mutability": "SEGMENTED",
                "data": {
                    "mention": {
                        "name": "funkymikky4ril",
                        "link": "funkymikky4ril@yahoo.com",
                        "avatar": "https://api.zuri.chat/files/profile_image/614679ee1a5607b13c00bcb7/6146fa49845b436ea04d10e9/20210928185128_0.jpg"
                    }
                }
            },
            "1": {
                "type": "emoji",
                "mutability": "IMMUTABLE",
                "data": {
                    "emojiUnicode": ":face_with_raised_eyebrow:"
                }
            }
        }
    }
}
"""

class Thread(MessageRequest):
    """Provide structure for the thread schema

    Class inherits from MessageRequest to hold
    data for the thread schema
    """

    room_id: str
    org_id: str
    message_id: str = Field(None, alias="_id")
    edited: bool = False

    @root_validator(pre=True)
    @classmethod
    def validates_message(cls, values):
        """Checks if the room_id and sender_id are valid

        Args:
            values [dict]: key value pair of sender and room id

        Returns:
            [dict]: key value pair of all object

        Raises:
            HTTPException [404]: if room_id or sender_id is invalid
        """

        sender_id = values.get("sender_id")
        org_id = values.get("org_id")
        room_id = values.get("room_id")
        with concurrent.futures.ThreadPoolExecutor(1) as executor:
            future = executor.submit(asyncio.run, get_room(org_id, room_id))
            room = future.result()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room not available"
            )

        if sender_id not in set(room["room_members"]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="sender not a member of this room",
            )
        return values


class Message(Thread):
    """Provides a base model for messages

    Message inherits from Thread
    and adds a field for list of threads
    """

    threads: List[Thread] = []
