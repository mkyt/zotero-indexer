#!/usr/bin/env python3
import sys
from pathlib import Path
import json

from extract import parse_pdf
from parse import integrate_library, save_docs

pdf_base = Path("/Users/hiro/Library/CloudStorage/OneDrive-Personal/ZotAttachments")
lib_base = Path("/Users/hiro/Downloads")

output_base = Path("./output")


if __name__ == "__main__":
    rdf = lib_base / "My Library.rdf"
    csl = lib_base / "My Library.json"

    if not output_base.exists():
        output_base.mkdir(exist_ok=True, parents=True)

    docs_f = output_base / "docs.json"

    if not docs_f.exists():
        docs = integrate_library(rdf, csl)
        save_docs(docs, docs_f)

    print("extracting fulltext from PDF...")
    path2fingerprints = {}
    docs = json.load(open(docs_f, "r"))
    for doc in docs:
        for attachment in doc["attachments"]:
            if attachment["type"] == "application/pdf":
                pdf_path = pdf_base / attachment["path"]
                fp = parse_pdf(pdf_path, output_base)
                if fp is not None:
                    path2fingerprints[attachment["path"]] = fp

    json.dump(
        path2fingerprints,
        open(output_base / "path2fingerprints.json", "w"),
        indent=2,
        ensure_ascii=False,
    )
