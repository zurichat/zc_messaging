# import os
# import zipfile
# import io
# import wget
# from typing import List
# from starlette.responses import Response


# def zipfiles(file_paths: List[str]):
# 	"""
# 		Helper Function for get_files function to retrieve images
# 		param:
# 			filepaths: list of lists of filepath
# 		returns:
# 			Archive file with images
# 	"""
# 	zip_subdir = "dummy_archive_path"
# 	zip_filename = "archive.zip"

# 	data = io.BytesIO()
# 	temp = zipfile.ZipFile(data, "w")
# 	for file_path in file_paths:
# 		file_dir, file_name = os.path.split(file_path )
# 		zip_path = os.path.join(zip_subdir, file_name)
# 		image_file = wget.download(file_path )
# 		temp.write(image_file, zip_path)

# 	temp.close()
# 	resp = Response(data.getvalue(), media_type="image/png-compressed", headers={
#         'Content-Disposition': f'attachment;filename={zip_filename}'
#     })

# 	return resp

from fastapi import HTTPException, UploadFile, status
from utils.file_storage import FileStorage


async def upload_files(token: str, attachments: list[UploadFile], org_id: str):
    """
    Uploads files to the file storage service

    Args:
        token (str): token for authentication with the file storage service
        attachments (list[UploadFile]): list of files to be uploaded
        org_id (str): organization id

    Raises:
        HTTPException [401]: Token is required for file storage service
        HTTPException [424]: File storage service is not available
        HTTPException [400]: Error uploading the file
    """    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Token is required for file storage service"
            },
        )

    file_store = FileStorage(organization_id=org_id)
    response = await file_store.files_upload(attachments, token)

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail={
                "status": "error",
                "message": "File storage service is not available"
            },
        )

    if isinstance(response, str):
        # Meaning there was an error uploading the file
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": response
            },
        )

    # Extract the urls from the response
    file_urls = [obj["file_url"] for obj in response]

    # NOTE: Currently, the file storage service returns a list of urls
    # that also contains the urls of the files that were previously
    # uploaded. So we need to remove those urls from the list
    return file_urls[len(file_urls) - len(attachments):]
