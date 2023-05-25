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