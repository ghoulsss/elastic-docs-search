import uvicorn
import asyncio
from fastapi import FastAPI
from api.upload import router as upload_router
from api.search import router as search_router
from s3.downloader_pdf import download_pdf_from_message
from services.elastic import create_index
from config import INDEX_NAME

print(INDEX_NAME)
app = FastAPI(title="PDF Search Service")

app.include_router(upload_router, prefix="/api")
app.include_router(search_router, prefix="/api")


# создаём индекс при старте
@app.on_event("startup")
async def startup_event():
    await create_index()


# if __name__ == "__main__":
# asyncio.run(download_pdf_from_message())
# uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
