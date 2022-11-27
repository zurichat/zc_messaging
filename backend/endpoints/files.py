from fastapi import  HTTPException, status
from schema.response import ResponseModel
from starlette.responses import JSONResponse, Response
from fastapi import FastAPI, UploadFile, File, APIRouter
from fastapi.responses import FileResponse, JSONResponse
from utils.message_utils import get_message, get_room_messages
from utils.files_utils import getImages
router = APIRouter()





@router.get("/org/{org_id}/rooms/{room_id}/files")
async def get_files(org_id: str, room_id: str):
	"""
		An endpoint that returns a list of images files uplaoded to th given room

		params:
		org_id: organization id number
		room_id: room id number
	"""

	room_messages = await get_room_messages(org_id, room_id)

    
	if not room_messages:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"No file was uploaded": room_messages},
		)

	list_files = []
	for message in room_messages:

		list_files.append(message['files'])

	return getImages(list_files)
	



   