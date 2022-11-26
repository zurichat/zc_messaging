from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from schema.message import Thread, MessageRequest, Message
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from utils.centrifugo import Events, centrifugo_client
from utils.message_utils import get_message, get_room_messages
from utils.message_utils import update_message_threads as edit_message_threads
from utils.room_utils import get_org_rooms
import json

router = APIRouter()

@router.put(
		"/org/{org_id}/rooms/{room_id}/messages/{message_id}/threads",
		response_model=ResponseModel,
		status_code=status.HTTP_200_OK,
		responses={
				401: {"description": "You are not authorized to edit this message"},
				404: {"description": "Message not found"},
				424: {"description": "Message not edited"},
		},
)
async def update_threads_message(
		org_id: str,
		room_id: str,
		message_id: str,
		request: MessageRequest,
		background_tasks: BackgroundTasks,
):
		"""Updates a message sent in a room.

		Edits an existing message document in the messages database collection while
		publishing to all members of the room in the background.

		Args:
				org_id: A unique identifier of the organization.
				room_id: A unique identifier of the room.
				message_id: A unique identifier of the message that is being edited.
				request: A pydantic schema that defines the message request parameters.
				background_tasks: A background task for publishing to all
													members of the room.

		Returns:
				A dict containing data about the message that was edited.

						{
								"_id": "61c3aa9478fb01b18fac1465",
								"created_at": "2021-12-22 22:38:33.075643",
								"edited": true,
								"emojis": [
								{
										"count": 1,
										"emoji": "👹",
										"name": "frown",
										"reactedUsersId": [
										"619ba4671a5f54782939d385"
										]
								}
								],
								"files": [],
								"org_id": "619ba4671a5f54782939d384",
								"richUiData": {
								"blocks": [
										{
										"data": {},
										"depth": 0,
										"entityRanges": [],
										"inlineStyleRanges": [],
										"key": "eljik",
										"text": "HI, I'm mark.. new here",
										"type": "unstyled"
										}
								],
								"entityMap": {}
								},
								"room_id": "619e28c31a5f54782939d59a",
								"saved_by": [],
								"sender_id": "619ba4671a5f54782939d385",
								"text": "string",
								"threads": []
						}

		Raises:
				HTTPException [401]: You are not authorized to edit this message.
				HTTPException [404]: Message not found.
				HTTPException [424]: Message not edited.
		"""

		payload = request.dict()

		loadedMessage = await get_message(org_id, room_id, message_id)

		loadedMessageThread = loadedMessage['threads']

		thread_to_add = {"threads": [payload, *loadedMessageThread]}

		if not loadedMessage:
				raise HTTPException(
						status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
				)
		

		added_thread_message = await edit_message_threads(org_id, message_id, thread_to_add)

		if not added_thread_message:
				raise HTTPException(
						status_code=status.HTTP_424_FAILED_DEPENDENCY,
						detail={"thread not added": added_thread_message},
				)

		# payload["edited"] = True
		loadedMessage.update(thread_to_add)

		# Publish to centrifugo in the background.
		background_tasks.add_task(
				centrifugo_client.publish,
				room_id, 
				Events.MESSAGE_UPDATE, 
				loadedMessage
		)

		return JSONResponse(
				content=ResponseModel.success(data=loadedMessage, message="Thread Added"),
				status_code=status.HTTP_200_OK,
		)
