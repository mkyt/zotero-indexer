#!/bin/bash
. .venv/bin/activate
meilisearch --master-key `cat API_KEY` &
python run_server.py