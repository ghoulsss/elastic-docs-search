import asyncio
import json
from services.s3 import download_file_from_s3
from services.pdf_processor import extract_pages
from services.elastic import index_document

async def process_message(body):
    payload = json.loads(body)

    document_id = payload["documentId"]
    s3_key = payload["s3Key"]

    file_path = f"/tmp/{document_id}.pdf"

    await download_file_from_s3(s3_key, file_path)
    pages = await extract_pages(file_path)
    await index_document(document_id, pages)


async def listen():
    print("Broker listener started")
    while True:
        await asyncio.sleep(1)
