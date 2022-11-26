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

    """
	An Endpoint that handles viewing image files uploaded in the DM

	params:
		org_id = Organisation id of user
		room_id = room id of user

	Retrieves All Messages in the Dm with the get_room_message method
	Handles  conditons for single and Multiple Uploaded Files
	"""
    room_messages = await get_room_messages(org_id, room_id)
    
    if not room_messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"No file was uploaded": room_messages},
        )

    messages_id_list =[]
    for message in room_messages:
        messages_id_list.append(message['_id'])

    
    temp = {}
    list_files = []
    for message_id in messages_id_list:
        temp.update(await get_message(org_id, room_id, message_id))
        for val in temp:
            list_files.append(temp["files"])



    return zipfiles(list_files)
# return a list of archived uploaded files


   