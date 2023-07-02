#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
import meilisearch
from pydantic import BaseModel
from typing import Any, Union

API_KEY = open("API_KEY").read().strip()

ms = meilisearch.Client("http://localhost:7700", API_KEY)
zotero_idx = ms.get_index("docs")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchQuery(BaseModel):
    q: Union[str, None]


@app.post("/_api/search")
def search(query: SearchQuery):
    if query.q is None:
        query.q = ""
    print("query:", query.q)

    res = []

    if query.q == "":
        return {"count": len(res), "data": res}

    search_results = zotero_idx.search(
        query.q,
        {
            "limit": 1000,
            "attributesToHighlight": ["*"],
            "attributesToCrop": ["fulltext.text"],
            "highlightPreTag": '<span class="highlight">',
            "highlightPostTag": "</span>",
            "matchingStrategy": "all",
        },
    )

    iid2fts: dict[str, list[Any]] = {}
    iid2md: dict[str, Any] = {}

    for hit in search_results["hits"]:
        iid: str = hit["item_id"]
        hit_doc = hit["_formatted"]
        if "metadata" in hit:
            iid2md[iid] = hit_doc
        elif "fulltext" in hit:
            if iid in iid2fts:
                iid2fts[iid].append(hit_doc)
            else:
                iid2fts[iid] = [hit_doc]

    only_in_fts = set(iid2fts.keys()).difference(set(iid2md.keys()))
    print(only_in_fts)
    mds = zotero_idx.get_documents(
        {
            "limit": 1000,
            "filter": f"record_type = metadata AND item_id IN [ {', '.join(only_in_fts)} ]",
        }
    )

    for d in mds.results:
        md = d.__dict__[
            "_Document__doc"
        ]  # slightly hacky way to get the underlying dict
        iid2md[md["item_id"]] = md

    for iid, md in iid2md.items():
        fts = iid2fts.get(iid, [])
        covers = md.get("attachment_fingerprints", [])
        cover_hash = covers[0] if len(covers) > 0 else None
        res.append(
            {
                "item_id": iid,
                "metadata": md["metadata"],
                "tags": md["tags"],
                "fulltext": fts,
                "cover_hash": cover_hash,
            }
        )

    return {"count": len(res), "data": res}


@app.get("/_api/cover/{hash}")
def cover(hash: str) -> Response:
    return FileResponse(f"output/{hash}/cover.jpg")


app.mount(
    "/", StaticFiles(directory="zotero-indexer-frontend/dist", html=True), name="static"
)
