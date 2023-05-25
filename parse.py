#!/usr/bin/env python3
import sys
from pathlib import Path
import json
import xml.etree.ElementTree as ET

doc_tags = set(
    [
        r"{http://purl.org/net/biblio#}Book",
        r"{http://purl.org/net/biblio#}Article",
        r"{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description",
    ]
)
coll_tag = r"{http://www.zotero.org/namespaces/export#}Collection"

title_tag = r"{http://purl.org/dc/elements/1.1/}title"
link_tag = r"{http://purl.org/rss/1.0/modules/link/}link"
resource_tag = r"{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
attachment_tag = r"{http://www.zotero.org/namespaces/export#}Attachment"
type_tag = r"{http://purl.org/rss/1.0/modules/link/}type"

about_key = r"{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
resource_key = r"{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"


def parse_rdf(f: Path):
    """Parse Zotero RDF file and return a list of documents with the following attributes:
    - id: str
    - title: str
    - attachments: list of dict with keys `path` and `type`
    - tags: set of str
    """
    lib_rdf = ET.parse(f)
    root = lib_rdf.getroot()
    item_id2node: dict[str, ET.Element] = {}

    docs: list[ET.Element] = []
    colls: list[ET.Element] = []

    for child in root:
        if about_key in child.attrib:
            item_id = child.attrib[about_key]
            item_id2node[item_id] = child
            # print(child.tag, item_id)
            if child.tag in doc_tags:
                docs.append(child)
            elif child.tag == coll_tag:
                colls.append(child)
        else:
            print("[ERROR] `about` attribute not found for top-level item!")
            print(child.tag, child.attrib)

    all_docs = []

    for doc in docs:
        item_id = doc.attrib[about_key]
        title = doc.find(title_tag).text
        attachments = []
        links = doc.findall(link_tag)
        for link in links:
            link_id = link.attrib[resource_key]
            link_node = item_id2node[link_id]
            if link_node.tag != attachment_tag:
                continue
            rsrc = link_node.find(resource_tag)
            if rsrc is None:
                print("[ERROR] `resource` tag not found for attachment!")
                continue
            resource_path = rsrc.attrib[resource_key]
            resource_path = resource_path.removeprefix("attachments:")

            typ = link_node.find(type_tag)
            if typ is None:
                print("[ERROR] `type` tag not found for attachment!")
                continue
            resource_type = typ.text
            attachments.append({"path": resource_path, "type": resource_type})
        all_docs.append(
            {
                "id": item_id,
                "title": title,
                "attachments": attachments,
                "tags": set(),
            }
        )

    docid2doc = {}
    for doc in all_docs:
        docid2doc[doc["id"]] = doc

    # collecion
    coll_dict = {}

    hasPart_tag = r"{http://purl.org/dc/terms/}hasPart"

    for coll in colls:
        coll_id = coll.attrib[about_key]
        title = coll.find(title_tag).text
        items = []
        children = []
        for part in coll.findall(hasPart_tag):
            part_id = part.attrib[resource_key]
            if part_id.startswith("#collection_"):
                children.append(part_id)
            elif part_id in docid2doc:
                items.append(part_id)
            else:
                print("[ERROR] unknown item id:", part_id)
        coll_dict[coll_id] = {
            "id": coll_id,
            "title": title,
            "items": items,
            "children": children,
        }

    # populate parent
    for coll in coll_dict.values():
        for child in coll["children"]:
            if child not in coll_dict:
                print("[ERROR] unknown collection id:", child)
            coll_dict[child]["parent"] = coll["id"]

    # derive full name
    def dfs(coll):
        if "parent" in coll:
            prefix = coll_dict[coll["parent"]]["full_name"] + "/"
        else:
            prefix = ""
        coll["full_name"] = prefix + coll["title"]
        for child in coll["children"]:
            dfs(coll_dict[child])

    for coll in coll_dict.values():
        if "parent" not in coll:  # depth 0 nodes
            dfs(coll)

    # populate tags for docs
    for coll in coll_dict.values():
        for item in coll["items"]:
            components = coll["full_name"].split("/")
            for i in range(len(components)):
                docid2doc[item]["tags"].add("/".join(components[: i + 1]))

    return all_docs


def parse_csl_json(f: Path):
    csl = json.load(open(f, "r"))
    keys_to_remove = ["id", "accessed", "source"]
    for item in csl:
        for key in keys_to_remove:
            if key in item:
                del item[key]
    return csl


def integrate_library(rdf_path, csl_path):
    docs = parse_rdf(rdf_path)
    csl = parse_csl_json(csl_path)
    t2csl = {}
    for item in csl:
        t2csl[item["title"]] = item

    for doc in docs:
        if doc["title"] not in t2csl:
            print("[ERROR] title not found in CSL:", doc["title"])
            continue
        csl_item = t2csl[doc["title"]]
        doc["metadata"] = csl_item

    return docs


class MyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)
        else:
            return json.JSONEncoder.default(self, o)


def save_docs(docs, f):
    json.dump(docs, open(f, "w"), indent=2, ensure_ascii=False, cls=MyEncoder)


def main():
    rdf, csl = sys.argv[1], sys.argv[2]
    rdf_path = Path(rdf)
    csl_path = Path(csl)
    docs = integrate(rdf_path, csl_path)
    save_docs(docs, "docs.json")


if __name__ == "__main__":
    main()
