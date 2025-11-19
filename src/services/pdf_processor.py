import aiofiles
import io
import PyPDF2
from pdf2image import convert_from_bytes
import pytesseract

async def extract_pages(file_path: str):
    pages = []

    # читаем PDF асинхронно
    async with aiofiles.open(file_path, "rb") as f:
        data = await f.read()

    pdf_stream = io.BytesIO(data)
    reader = PyPDF2.PdfReader(pdf_stream)

    images = convert_from_bytes(data)

    for num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if len(text.strip()) < 5:
            ocr_text = pytesseract.image_to_string(images[num - 1], lang="rus")
            if ocr_text.strip():
                text = ocr_text

        pages.append({
            "pageNum": num,
            "pageSummary": text.strip()
        })

    return pages
