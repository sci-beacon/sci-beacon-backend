#!/bin/bash

uvicorn questionbank_launch:app --port 5501 --env-file dev.env --root-path /sci-beacon-backend
