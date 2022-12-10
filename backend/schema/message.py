import asyncio
import concurrent.futures
import inspect
from datetime import datetime
from typing import Any, List, Type

from fastapi import Form, HTTPException, status
from pydantic import AnyHttpUrl, BaseModel, Field, Json, root_validator
from utils.room_utils import get_room


class Emoji(BaseModel):
    """
    Provides the nested object for reactions to message
    """

    name: str
    count: int
    emoji: str
    reactedUsersId: List[str] = []


class MessageRequest(BaseModel):
    """
    Provides a base model for all threads

    This is the message model that will be used to create a message
    {
        "message_id": "1640204440922",
        "sender_id": "619ba4671a5f54782939d385",
        "timestamp": 1640204440922,
        "emojis": [],
        "richUiData": {
            "blocks": [
                {
                    "key": "f3s6p",
                    "text": "@funkymikky4ril HI, I'm mark.. new here",
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
                            "avatar": "https://api.zuri.chat/files/profile_image/6146/1e9/208_0.jpg"
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
        },
        "files": ["https://api.zuri.chat/files/profile_image/614679ee1a5607b13c00bcb7/6146f"],
        "saved_by": []
        "created_at": "2021-12-22 22:38:33.075643"
    }

    """

    sender_id: str
    emojis: List[Emoji] = []
    richUiData: Any = {}
    files: List[AnyHttpUrl] = []
    saved_by: List[str] = []
    timestamp: int = 0
    created_at: str = str(datetime.utcnow())

    @classmethod
    def as_form(
        cls,
        sender_id: str = Form(str),
        emojis: List[Emoji] = Form([]),
        richUiData: Any = Form({}),
        files: List[AnyHttpUrl] = Form([]),
        saved_by: List[str] = Form([]),
        timestamp: int = Form(int),
        created_at: str = Form(str(datetime.utcnow())),
    ):
        return cls(
            sender_id=sender_id,
            emojis=emojis,
            richUiData=richUiData,
            files=files,
            saved_by=saved_by,
            timestamp=timestamp,
            created_at=created_at
        )


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
                status_code=status.HTTP_404_NOT_FOUND, detail="Room does not exist"
            )

        if sender_id not in set(room["room_members"]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not a member of this room",
            )
        return values


class Message(Thread):
    """Provides a base model for messages

    Message inherits from Thread
    and adds a field for list of threads
    """

    threads: List[Thread] = []


# NOTE: The reason for this is because fastapi does not support
# multipart/form-data requests with pydantic models
# https://github.com/tiangolo/fastapi/issues/2387
# used: https://github.com/tiangolo/fastapi/issues/2387#issuecomment-731662551
def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models.
    The as_form class method can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls


@as_form
class MessageFormData(MessageRequest):
    richUiData: Json[Any] = "{}"
    emojis: Json[list[Emoji]] = "[]"
    files: Json[list[AnyHttpUrl]] = "[]"
    saved_by: Json[list[str]] = "[]"
