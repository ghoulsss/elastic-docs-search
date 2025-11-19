import aiofiles
from fastapi import APIRouter, UploadFile, Form
from services.pdf_processor import extract_pages
from services.elastic import index_document

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile, documentId: str = Form(...)):
    # сохраняем временно PDF
    file_path = f"/tmp/{file.filename}"
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    pages = await extract_pages(file_path)
    document = {"documentId": documentId, "pages": pages}

    await index_document(document)
    return {"status": "ok", "documentId": documentId, "pages": len(pages)}
