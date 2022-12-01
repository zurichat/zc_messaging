# import os
# import zipfile
# import io
# import wget
# from starlette.responses import Response
from pydantic import AnyHttpUrl
from utils.file_storage import FileStorage

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


async def upload_files(
	org_id: str, file: object, token: str
) -> list[AnyHttpUrl or None]:
	"""Handles file upload to zc_core.

	Args:
		file (object): file object to be uploaded.
		token (str): The user's token.

	Returns:
		On success, a list containing the file url of the uploaded file.
		_type_: list[AnyHttpUrl], None]

		On errror, returns an empty list
    """
	file_object = [
		('file', (f'{file.filename}', f'{file.file}', f'{file.content_type}'))
	]

	FS = FileStorage(org_id)
	file_url = await FS.files_upload(file_object, token)

	if file_url:
		return [file_url]
	return []
