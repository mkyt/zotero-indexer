import unicodedata
import json
import re

import fitz
from dehyphen import FlairScorer, text_to_format
import langdetect

scorer = FlairScorer(lang="en", fast=True)


def to_plain(lst):
    res = []
    for l1 in lst:
        for l2 in l1:
            for word in l2:
                res.append(word)
    return " ".join(res).replace("  ", " ")


def dehyphen(t):
    t = re.sub(
        r"\n\s+\n", "\n\n", t, flags=re.MULTILINE
    )  # remove empty lines with spaces
    fmt = text_to_format(t)
    fixed_hyphens = scorer.dehyphen(fmt)
    return to_plain(fixed_hyphens)


def remove_newline(t):
    lines = t.split("\n")
    for i in range(len(lines) - 1):
        if (
            len(lines[i]) > 0
            and lines[i][-1].isascii()
            and len(lines[i + 1]) > 0
            and lines[i + 1][0].isascii()
        ):
            lines[i] += " "
    return "".join(lines).replace("  ", " ")


def extract_text(doc):
    lang = None
    res = []
    for i, page in enumerate(doc):
        t = page.get_text()
        t = unicodedata.normalize("NFKC", t)
        try:
            lang = langdetect.detect(t)
        except:
            lang = "unknown"

        if lang == "en":
            t = dehyphen(t)
        elif lang == "ja":
            t = remove_newline(t)

        res.append({"page": i + 1, "text": t})
    return res


def get_fingerprint(doc: fitz.Document) -> str:
    """Return a fingerprint of the document, which consists of a hash of the first page's rendered image and the number of pages."""
    fp = doc[0]
    return fp.get_pixmap(dpi=36, annots=False).digest.hex() + f"{len(doc):04x}"


def parse_pdf(path, output_base) -> str:
    doc = fitz.open(path)
    if len(doc) == 0:
        return None
    fingerprint = get_fingerprint(doc)
    print('processing "{}" ({})...'.format(path, fingerprint))

    p = output_base / fingerprint
    if p.exists() and (p / "text.json").exists() and (p / "cover.jpg").exists():
        print(f"[INFO] {path} already exists, skipping")
        return fingerprint
    p.mkdir(parents=True, exist_ok=True)

    total_pages = len(doc)
    pages = extract_text(doc)
    json.dump(
        {
            "pages": pages,
            "total_pages": total_pages,
            "path": str(path),
        },
        open(p / "text.json", "w"),
        indent=2,
        ensure_ascii=False,
    )

    frontpage = doc[0]
    pix = frontpage.get_pixmap(dpi=72)
    pix.pil_save(p / "cover.jpg", dpi=(72, 72))

    return fingerprint
