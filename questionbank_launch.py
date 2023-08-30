import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from brotli_asgi import BrotliMiddleware

root = os.path.dirname(__file__)

#########################################################

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Enable Brotli compression
app.add_middleware(BrotliMiddleware)


#########################################################
# IMPORT MODULES

import dbconnect
import api_questions
import api_topics
import api_files
import api_export
