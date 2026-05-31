from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings
from app.services.embedder import EMBEDDING_DIM

client = QdrantClient(url=settings.QDRANT_URL)


def ensure_collection():
    existing = [c.name for c in client.get_collections().collections]
    if settings.QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
        print(f"Created Qdrant collection: {settings.QDRANT_COLLECTION}")


def store_chunks(chunks: list[dict]):
    points = []
    for chunk in chunks:
        points.append(
            PointStruct(
                id=_chunk_id_to_int(chunk["id"]),
                vector=chunk["embedding"],
                payload={
                    "text": chunk["text"],
                    "doc_id": chunk["doc_id"],
                    "filename": chunk["filename"],
                    "page": chunk["page"],
                    "chunk_index": chunk["chunk_index"],
                },
            )
        )

    client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=points,
    )


def search_chunks(query_vector: list[float], top_k: int = 5) -> list[dict]:
    results = client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "text": r.payload["text"],
            "doc_id": r.payload["doc_id"],
            "filename": r.payload["filename"],
            "page": r.payload["page"],
            "score": r.score,
        }
        for r in results
    ]


def delete_document(doc_id: str):
    client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[
                FieldCondition(key="doc_id", match=MatchValue(value=doc_id))
            ]
        ),
    )


def _chunk_id_to_int(chunk_id: str) -> int:
    return abs(hash(chunk_id)) % (10**15)