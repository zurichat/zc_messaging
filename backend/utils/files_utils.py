import os
import zipfile
import io


def zipfiles(filenames: str):

	"""
		An Helper function to help handling of multiple file
	"""
	
	zip_subdir = "dummy_archive_path"
	zip_filename = "archive.zip"
	
		# filenames = ["dummy_url path1", "dummy_url path12" ]

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

	return resp