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
	
