from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from schema.room import RoomType
from schema.response import ResponseModel
from starlette.responses import JSONResponse
from fastapi import FastAPI, UploadFile, File
from os import getcwd
from fastapi.responses import FileResponse, JSONResponse
from .messages import get_messages
app = FastAPI()

# @app.post("/upload/{user_id}/{DM}/files/{file_name}")
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with open(file.filename, 'wb') as image:
        content = await file.read()
        image.write(content)
        image.close()
    return JSONResponse(content={"filename": file.filename},
status_code=200)

# @app.get("/download/{user_id}/{DM}/files/{file_name}")
@app.get("/download/{file_name}")
def download_file(file_name: str):
    return FileResponse(path=getcwd() + "/" + file_name,
     media_type='application/octet-stream', filename=file_name)


# need to verify the dm_install plugin method in sync.py
# dm_install(org_id, room_name:user_id)

@app.get("/get/files/{org_id}/{room_id}")
def get_files(org_id: str, room_id: str):
    files = []
    messages = get_messages(org_id, room_id)
    # print(messages.files)
    # if messages.files:
    #     for file in messages.files:
    #         pass
    #         # if file is media : do this
    #         # if file is text file : do this
    #         # if file is audio: do this
    # else:
    #     return

    
    # try:
    #     pass
    # except requests.exceptions.RequestException:
    #     return None

    # if response.status_code == 200:
    #         return FileResponse(path=getcwd() + "/" + file_name)
    