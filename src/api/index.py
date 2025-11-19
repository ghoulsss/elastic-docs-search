from fastapi import APIRouter, UploadFile, Form
from services.elastic import create_index, delete_index

router = APIRouter()


# -------------------------
# Создание индекса
# -------------------------
@router.post("/create")
async def create_index_route():
    await create_index()
    return {"status": "ok", "message": "Index created"}


# -------------------------
# Удаление индекса
# -------------------------
@router.delete("/delete")
async def delete_index_route():
    await delete_index()
    return {"status": "ok", "message": "Index deleted"}
