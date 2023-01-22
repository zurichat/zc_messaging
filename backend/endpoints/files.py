# from fastapi import HTTPException, status
# from fastapi import APIRouter
# from utils.message_utils import get_room_messages
# from utils.files_utils import zipfiles

# router = APIRouter()


# @router.get("/org/{org_id}/rooms/{room_id}/files")
# async def get_files(org_id: str, room_id: str, page: int = 1,limit:int=15):
#     """
#     An endpoint that returns a list of images files uplaoded to th given room

#     params:
#             org_id: organization id number: "6373eb474746182adae97314",
#             room_id: room id number: "6373eb4f4746182adae97316"
#     return:
#             A list of filepaths urls
#     """

#     room_messages = await get_room_messages(org_id, room_id, page, limit)

#     if not room_messages:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail={"No file was uploaded": room_messages},
#         )

#     file_paths = []

#     for message in room_messages:
#         if len(message["files"]):
#             file_paths = file_paths + message["files"]

#     return zipfiles(file_paths)
