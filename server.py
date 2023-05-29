from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import meilisearch
from typing import Union


app = FastAPI()


@app.post("/_api/search")
def search(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/_api/cover/{hash}")
def cover(hash: str):
    return FileResponse(f"output/{hash}/cover.jpg")


app.mount(
    "/", StaticFiles(directory="zotero-indexer-frontend/dist", html=True), name="static"
)
