#!/usr/bin/env python3
import meilisearch
from pathlib import Path
import json
import base64


API_KEY = open("API_KEY").read().strip()
INDEX_NAME = "docs"


def get_client():
    return meilisearch.Client("http://localhost:7700", API_KEY)


def create_index():
    c = get_client()
    task = c.create_index(INDEX_NAME)
    result = c.wait_for_task(task.task_uid)
    print(result)


def setup_index():
    c = get_client()
    index = c.get_index(INDEX_NAME)
    task = index.update_settings(
        {
            "filterableAttributes": ["item_id", "record_type", "tags", "metadata.type"],
            "typoTolerance": {
                "enabled": False,
            },
        }
    )
    result = c.wait_for_task(task.task_uid, 300000)  # 5 min.
    print(result)


def construct_records(output_base: Path):
    # one document in Zotero corresponds to several documents in MeiliSearch index
    # - one document for metadata (whose id is the same as the id of the document in Zotero)
    # - one document for each page of the attachment(s) (whose id is the same as the id of the document in Zotero + page number)

    # schema for metadata
    # - id: str
    # - item_id: str
    # - tags: list of str
    # - metadata: object

    # schema for fulltext
    # - id: str
    # - item_id: str
    # - fingerprint: str
    # - total_pages: int
    # - fulltext.page: int
    # - fulltext.text: str

    docs = json.load(open(output_base / "docs.json"))
    path2fingerprints = json.load(open(output_base / "path2fingerprints.json"))

    records = {}
    for doc in docs:
        attachment_fingerprints: list[str] = []
        item_id = (
            base64.b64encode(doc["id"].encode(), altchars=b"_-")
            .decode()
            .replace("=", "")
        )
        for a in doc["attachments"]:
            if a["path"] not in path2fingerprints:
                continue
            fp = path2fingerprints[a["path"]]
            t = output_base / fp / "text.json"
            if not t.exists():
                continue
            attachment_fingerprints.append(fp)
            text = json.load(open(t))
            for page in text["pages"]:
                did = f"{fp}-{page['page']:05d}"
                records[did] = {
                    "id": did,
                    "item_id": item_id,
                    "record_type": "fulltext",
                    "fingerprint": fp,
                    "total_pages": text["total_pages"],
                    "fulltext": {
                        "page": page["page"],
                        "text": page["text"],
                        "guessed_lang": page["guessed_lang"],
                    },
                }

        # metadata
        records[item_id] = {
            "id": item_id,
            "item_id": item_id,
            "record_type": "metadata",
            "tags": list(doc["tags"]),
            "metadata": doc["metadata"],
            "attachment_fingerprints": attachment_fingerprints,
        }

    return records


def deepdiff(a, b):
    if isinstance(a, dict):
        if not isinstance(b, dict):
            return True
        for k in a:
            if k not in b:
                return True
            if deepdiff(a[k], b[k]):
                return True
        return False
    elif isinstance(a, list):
        if not isinstance(b, list):
            return True
        if len(a) != len(b):
            return True
        for i in range(len(a)):
            if deepdiff(a[i], b[i]):
                return True
        return False
    else:
        return a != b


def get_diff(new_records, old_records):
    res = []

    for key, record in new_records.items():
        if key not in old_records:
            res.append(("add", key))
        elif deepdiff(record, old_records[key]):
            res.append(("update", key))
    removed = set(old_records.keys()) - set(new_records.keys())
    for key in removed:
        res.append(("remove", key))

    return res


def main():
    output_base = Path("./output")
    records = construct_records(output_base)
    old_records_json = output_base / "records_backup.json"
    if old_records_json.exists():
        old_records = json.load(open(output_base / "records_backup.json"))
    else:
        old_records = {}

    changes = get_diff(records, old_records)

    to_add_or_replace = []
    to_remove = []
    for cmd, doc_id in changes:
        if cmd in ("add", "update"):
            to_add_or_replace.append(records[doc_id])
        elif cmd == "remove":
            to_remove.append(doc_id)

    c = get_client()
    ok = True
    if len(to_add_or_replace) > 0:
        print("adding or replacing {} document(s)...".format(len(to_add_or_replace)))
        task = c.index(INDEX_NAME).add_documents(to_add_or_replace, primary_key="id")
        result = c.wait_for_task(task.task_uid, 300000)  # timeout = 5 min.
        print(result)
        if result.status != "succeeded":
            ok = False
    if len(to_remove) > 0:
        print("removing {} document(s)...".format(len(to_remove)))
        task = c.index(INDEX_NAME).delete_documents(to_remove)
        result = c.wait_for_task(task.task_uid)
        print(result)
        if result.status != "succeeded":
            ok = False

    if ok:
        print('operation succeeeded, saving "records_backup.json"...')
        json.dump(
            records,
            open(output_base / "records_backup.json", "w"),
            indent=2,
            ensure_ascii=False,
        )


def check_tasks():
    c = get_client()
    tasks = c.get_tasks()
    print(tasks)


def initialize():
    create_index()
    setup_index()


if __name__ == "__main__":
    initialize()
    main()
