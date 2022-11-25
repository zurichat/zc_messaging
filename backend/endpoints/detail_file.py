from fastapi import APIRouter, UploadFile,  status
from fastapi.responses import FileResponse
from utils.message_utils import get_message
from starlette.responses import JSONResponse
router = APIRouter()

# org_id :6373eb474746182adae97314
# room_id: 6373eb4f4746182adae97316
# message_id:637fe320601ce3fc5dc739ea


@router.get("/org/{org_id}/rooms/{room_id}/messages/{message_id}")
async def get_detail(org_id: str, room_id: str, message_id: str):
    messages = await get_message(org_id, room_id, message_id)
    try:
        content = {"files": messages['files']}
        status_code = status.HTTP_200_OK
    except:
        content = {"detail": "invalid request"}
        status_code = status.HTTP_400_BAD_REQUEST
    return JSONResponse(
        content=content,
        status_code=status_code
    )
