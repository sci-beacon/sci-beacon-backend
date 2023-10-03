# api_files.py
import uuid
import os

from fastapi import HTTPException, Header, File, UploadFile, Form
from pydantic import BaseModel
from typing import List
from PIL import Image, ImageOps

import dbconnect
from questionbank_launch import app
import commonfuncs as cf

root = os.path.dirname(__file__)
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER","data/uploads")
uploadFolder = os.path.join(root, UPLOAD_FOLDER)
os.makedirs(uploadFolder, exist_ok=True)

######################################
# FUNCTIONS


def saveImage(f, idf):
    # instead of re-reading image from disk, taking the file pointer already loaded in memory.
    global uploadFolder
    im = Image.open(f, mode='r')
    im1 = ImageOps.exif_transpose(im) # auto-rotate mobile photos. from https://stackoverflow.com/a/63798032/4355695
    
    # save picture, but downsized to 2000x2000 dimensions (in case its big) to optimize storage
    w, h = im1.size
    if(h > 1000 or w > 1000):
        im3 = ImageOps.contain(im1, (1000,1000))
        im3.save(os.path.join(uploadFolder, idf))
    else:
        im1.save(os.path.join(uploadFolder, idf), "WEBP")
        # save it in webp format regardless of what uploaded format was

    return

def image_size(filename):
    with Image.open(filename, mode='r') as im:
         width, height = im.size
    return width, height


######################################
# API CALLS
@app.post("/api/files/upload", tags=["files"])
def uploadFile(
        uploadFiles: List[UploadFile] = File(...)
    ):
    # to do: process and save file; return id
    file1 = uploadFiles[0]
    filename = file1.filename
    extension = filename.split('.')[-1].lower()
    # validate extension
    if extension not in ('jpg','png','jpeg','webp'):
        raise HTTPException(status_code=400, detail="Invalid files")
    
    new_filename = f"{str(uuid.uuid4())}.webp"

    saveImage(file1.file, new_filename)

    returnD = {"filename": new_filename}
    return returnD