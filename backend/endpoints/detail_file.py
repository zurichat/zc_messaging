from fastapi import APIRouter,  status, HTTPException
from utils.message_utils import get_message
import requests

router = APIRouter()

@router.get("/org/{org_id}/rooms/{room_id}/messages/{message_id}")
async def details_of_file(org_id: str, room_id: str, message_id: str):
    """
	An endpoint that returns the details of a file uplaoded to the given room
	params:
		org_id: organization id number
		room_id: room id number
        message_id: message id number
		return:
			The details of a file uploaded

    org_id :6373eb474746182adae97314
    room_id: 6373eb4f4746182adae97316
    message_id:638229130ff68071db65aea6
"""
    message = await get_message(org_id, room_id, message_id)
    
    if not message:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="message not found"
        )
    details = []

    files = message.get('files')
  
    for file in files:
        my_file = requests.get(file)

        file_size = round(len(my_file.content)/1000, 1)
        file_name_split = file.split("/")
        file_name = file_name_split[len(file_name_split) - 1].split(".")[0]
        file_type = my_file.headers.get("content-type").split("/")[1]

        details_of_file = {
                    "file-name" : file_name,
                    "file-type" : file_type,
                    "file-size" : f"{file_size}kb"
            }
        details.append(details_of_file)

    return details
 