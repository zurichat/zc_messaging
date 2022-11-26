from fastapi import  HTTPException, status
from schema.response import ResponseModel
from starlette.responses import JSONResponse, Response
from fastapi import FastAPI, UploadFile, File, APIRouter
from fastapi.responses import FileResponse, JSONResponse
from utils.message_utils import get_message, get_room_messages
import os
import zipfile
import io
from zipfile import ZipFile
router = APIRouter()

"""
 A get method endpoint to Handle retrieving and Viewing of uploaded files in a DM

"""

# {
#     "organization_id" :"6373eb474746182adae97314",
#     "room_id" : "6373eb4f4746182adae97316"

        #         org_id:
        # 6373eb474746182adae97314
        # room_id:
        # 6373eb4f4746182adae97316

        #  Use:
        # org_id: 619ba4
        # room_id: 123456
# }


def zipfiles(filenames: str):
    zip_subdir = "dummy_archive_path"
    zip_filename = "archive.zip"
    """
        filenames = ["dummy_url path1", "dummy_url path12" ]
    """
    data = io.BytesIO()
    temp = zipfile.ZipFile(data, "w")

    for filepath in filenames:
        fdir, fname = os.path.split(filepath)
        zip_path = os.path.join(zip_subdir, fname)
        temp.write(fdir, zip_path)

    temp.close()
    resp = Response(data.getvalue(), media_type="image/png-compressed", headers={
        'Content-Disposition': f'attachment;filename={zip_filename}'
    })

    return response


"""
An Endpoint that handles viewing image files uploaded in the DM

params:
    org_id = Organisation id of user
    room_id = room id of user

Retrieves All Messages in the Dm with the get_room_message method
Handles  conditons for single and Multiple Uploaded Files
"""

@router.get("/org/{org_id}/rooms/{room_id}/files")
async def get_files(org_id: str, room_id: str):
    """
    gets a list of dicts of room messages with the get_room_messages method
    
    Returns:
        A list of Uploaded files for each message id in the room
    """
    room_messages = await get_room_messages(org_id, room_id)
    
    if not room_messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"No file was uploaded": room_messages},
        )

    id_list =[]
    for msg in room_messages:
        id_list.append(msg['_id'])

    
    temp = {}
    list_files = []
    for id in id_list:
        temp.update(await get_message(org_id, room_id, id))
        for val in temp:
            list_files.append(temp["files"])

    return zipfiles(list_files)
# return a list of archived uploaded files





    
   