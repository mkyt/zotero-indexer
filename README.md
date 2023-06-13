# zotero-indexer

Index your zotero-managed bibliographies to meilisearch to enable full-text search!


## Workflow

1. Export CSL-JSON and RDF from Zotero (from Menu -> File -> Export Library...)
2. Match metadata from CSL-JSON and PDF file paths from RDF
3. Extract PDF full-text and cover image using `pikepdf`
4. Index metadata and fulltext to Meilisearch

## Details

- Item: One entry in Zotero, keyed by `BibArticle` id on the RDF side
- File: A file attached to an item (can be many)


## Index

Index `uid`: "documents"

Item Schema:

```json
{
    'doc_id': string, // base64-encoded document id
    'id': string, // index item id sha1sum(`doc_id`+'_metadata' or `doc_id`+'_'+file_path+'pagenumber'`)
    'metadata'
    'fulltext': {
        'text'
        'pagenumber'
        'totalpages'
        'file':
    }
}
```


## How to use

### Create / Update Index

```bash
source .venv/bin/activate

# create json dump for fulltext and metadata
python ./main.py

# index to meilisearch
meilisearch --master-key LaZbmSrq-RBIV3GfQJM8KgryLva2gMo4Wzf4gRQxcis
python ./index.py

```

## Search frontend
```bash
meilisearch --master-key LaZbmSrq-RBIV3GfQJM8KgryLva2gMo4Wzf4gRQxcis
uvicorn server:app --reload
```

### Develop Frontend

```bash

# start meilisearch and backend python server
meilisearch --master-key LaZbmSrq-RBIV3GfQJM8KgryLva2gMo4Wzf4gRQxcis
uvicorn server:app --reload

cd zotero-indexer-frontend
npm install
npm run dev

npm build

```

