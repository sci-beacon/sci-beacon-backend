#!/bin/bash

export DB_FILENAME=questionbank.db
export DB_FOLDER=data/database
export UPLOAD_FOLDER=data/uploads
export EXPORT_FOLDER=data/exports

uvicorn questionbank_launch:app --port 5501 --reload

