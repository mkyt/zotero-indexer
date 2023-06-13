#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
import meilisearch
from typing import Union

API_KEY = open("API_KEY").read().strip()

ms = meilisearch.Client("localhost:7700", API_KEY)

app = FastAPI()


@app.post("/_api/search")
def search():
    return {"item_id": item_id, "q": q}


@app.get("/_api/cover/{hash}")
def cover(hash: str) -> Response:
    return FileResponse(f"output/{hash}/cover.jpg")


app.mount(
    "/", StaticFiles(directory="zotero-indexer-frontend/dist", html=True), name="static"
)
