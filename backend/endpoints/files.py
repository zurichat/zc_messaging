from fastapi import  HTTPException, status
from schema.response import ResponseModel
from starlette.responses import JSONResponse, Response
from fastapi import FastAPI, UploadFile, File, APIRouter
from fastapi.responses import FileResponse, JSONResponse
from utils.message_utils import get_message, get_room_messages
from utils.files_utils import zipfiles
router = APIRouter()





@router.get("/org/{org_id}/rooms/{room_id}/files")
async def get_files(org_id: str, room_id: str):
    

	room_messages = await get_room_messages(org_id, room_id)
	# return room_messages
    
	if not room_messages:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"No file was uploaded": room_messages},
		)


	list_files = []
	for message in room_messages:

		list_files.append(message['files'])

	return zipfiles(list_files)
	
        


	

    # return list_files
# return a list of archived uploaded files


   