export default function getCoverImageURL(doc) {
  if (!doc.cover_hash) {
    return null;
  } else {
    return '//localhost:8000/_api/cover/' + doc.cover_hash;
  }
}