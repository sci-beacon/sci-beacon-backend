import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from brotli_asgi import BrotliMiddleware
from fastapi.staticfiles import StaticFiles  # static html files deploying
import logging

root = os.path.dirname(__file__)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    # level=logging.INFO,
    filename=os.path.join(root, 'logs', "log.txt"),
)

#########################################################

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Enable Brotli compression
app.add_middleware(BrotliMiddleware)


#########################################################
# IMPORT MODULES

import dbconnect
import api_questions
import api_topics
import api_files
import api_export
import api_users

root = os.path.dirname(__file__)
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "data/uploads")
uploadFolder = os.path.join(root, UPLOAD_FOLDER)

EXPORT_FOLDER = os.environ.get("EXPORT_FOLDER", "data/exports")
exportFolder = os.path.join(root, EXPORT_FOLDER)

app.mount("/images", StaticFiles(directory=uploadFolder, html=False), name="images")
app.mount("/exports", StaticFiles(directory=exportFolder, html=False), name="exports")
