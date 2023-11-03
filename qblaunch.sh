#!/bin/bash

uvicorn questionbank_launch:app --port 5501 --reload --env-file dev.env
