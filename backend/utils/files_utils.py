import os
import zipfile
import io
from typing import List

from fastapi import Response



def zipfiles(filenames: str):

	filepaths = [" ".join(item)  for item in filenames]


	list_of_images = []
	for filepath in filepaths:
		if filepath:
			list_of_images.append(filepath)

	return list_of_images
