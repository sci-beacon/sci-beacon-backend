#!/bin/bash

export DB_FILENAME=questionbank.db
export DB_FOLDER=data/database
export UPLOAD_FOLDER=data/uploads
export EXPORT_FOLDER=data/exports
export DB_FILENAME_ADMIN=admin.db
export DB_SCHEMAFILE=dbschema.sql
export DB_SCHEMAFILE_ADMIN=dbschema-admin.sql


uvicorn questionbank_launch:app --port 5501 --reload

