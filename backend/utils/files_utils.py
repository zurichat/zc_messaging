import os
import zipfile
import io
import wget
from starlette.responses import StreamingResponse, Response



def zipfiles(filenames: str):
	"""
		Helper Function for get_files function to retrieve images
		param:
			filenames: list of lists of filepath
		returns:
			Archive file with images
	"""
	zip_subdir = "dummy_archive_path"
	zip_filename = "archive.zip"

	data = io.BytesIO()
	temp = zipfile.ZipFile(data, "w")
	for filepath in filenames:
		fdir, fname = os.path.split(filepath)
		zip_path = os.path.join(zip_subdir, fname)
		image_file = wget.download(filepath)
		temp.write(image_file, zip_path)

	temp.close()
	resp = Response(data.getvalue(), media_type="image/png-compressed", headers={
        'Content-Disposition': f'attachment;filename={zip_filename}'
    })

	return resp
	
	