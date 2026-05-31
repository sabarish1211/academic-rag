from fastapi import APIRouter, HTTPException, UploadFile, File

from app.services.ingestion import ingest_document
from app.services.vector_store import delete_document

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".pptx", ".ppt"}
MAX_FILE_SIZE_MB = 50


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}",
        )

    file_bytes = await file.read()

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB",
        )

    try:
        result = ingest_document(filename=filename, file_bytes=file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    return {
        "message": "Document ingested successfully",
        "doc_id": result["doc_id"],
        "filename": result["filename"],
        "pages_processed": result["pages"],
        "chunks_stored": result["chunks"],
    }


@router.delete("/{doc_id}")
async def remove_document(doc_id: str):
    try:
        delete_document(doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Document {doc_id} deleted successfully"}