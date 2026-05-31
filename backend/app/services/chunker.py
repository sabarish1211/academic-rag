from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


def chunk_pages(pages: list[dict], doc_id: str, filename: str) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    chunk_index = 0

    for page in pages:
        page_chunks = splitter.split_text(page["text"])

        for chunk_text in page_chunks:
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue

            chunks.append({
                "id": f"{doc_id}-{chunk_index}",
                "text": chunk_text,
                "doc_id": doc_id,
                "filename": filename,
                "page": page["page"],
                "chunk_index": chunk_index,
            })
            chunk_index += 1

    return chunks