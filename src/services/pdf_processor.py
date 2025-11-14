import aiofiles
import io
import PyPDF2

async def extract_pages(file_path: str):
    pages = []

    # читаем PDF асинхронно
    async with aiofiles.open(file_path, "rb") as f:
        data = await f.read()

    pdf_stream = io.BytesIO(data)
    reader = PyPDF2.PdfReader(pdf_stream)

    for num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({
            "pageNum": num,
            "pageSummary": text
        })

    return pages
