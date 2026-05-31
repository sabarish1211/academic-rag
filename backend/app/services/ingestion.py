import uuid

from app.services.chunker import chunk_pages
from app.services.embedder import embed_chunks
from app.services.parser import parse_document
from app.services.vector_store import store_chunks


def ingest_document(filename: str, file_bytes: bytes) -> dict:
    doc_id = str(uuid.uuid4())

    print(f"[ingest] Starting: {filename} (doc_id={doc_id})")

    # Step 1: Parse
    pages = parse_document(filename, file_bytes)
    print(f"[ingest] Parsed {len(pages)} pages/slides")

    if not pages:
        raise ValueError("No text could be extracted from this document.")

    # Step 2: Chunk
    chunks = chunk_pages(pages, doc_id=doc_id, filename=filename)
    print(f"[ingest] Created {len(chunks)} chunks")

    # Step 3: Embed
    chunks = embed_chunks(chunks)
    print(f"[ingest] Generated embeddings for {len(chunks)} chunks")

    # Step 4: Store
    store_chunks(chunks)
    print(f"[ingest] Stored in Qdrant ✓")

    return {
        "doc_id": doc_id,
        "filename": filename,
        "pages": len(pages),
        "chunks": len(chunks),
    }