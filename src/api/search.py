from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.elastic import es, INDEX_NAME

router = APIRouter()

class SearchRequest(BaseModel):
    searchQuery: str

# ------------------------------
# Endpoint 1: вывести все документы
# ------------------------------
@router.get("/documents")
async def get_all_documents():
    resp = await es.search(
        index=INDEX_NAME,
        query={"match_all": {}},
        size=100  # можно увеличить если нужно
    )
    results = []
    for hit in resp["hits"]["hits"]:
        results.append(hit["_source"])
    return {"count": len(results), "documents": results}

# ------------------------------
# Endpoint 2: поиск по тексту страниц
# ------------------------------
@router.post("/search")
async def search_documents(payload: SearchRequest):
    query_text = payload.searchQuery

    resp = await es.search(
        index=INDEX_NAME,
        query={
            "nested": {
                "path": "pages",
                "query": {
                    "match": {
                        "pages.pageSummary": query_text
                    }
                },
                "inner_hits": {}  # чтобы вернуть только страницы с результатом
            }
        },
        size=50  # сколько документов вернуть максимум
    )

    results = []
    for hit in resp["hits"]["hits"]:
        doc_score = hit["_score"]

        doc = {"documentId": hit["_source"]["documentId"],
               "documentScore": doc_score,
               "pages": [],}
        inner_hits = hit.get("inner_hits", {})
        pages_hits = inner_hits.get("pages", {}).get("hits", {}).get("hits", [])
        for p in pages_hits:
            doc["pages"].append(p["_source"])
        results.append(doc)

    return {"count": len(results), "results": results}

@router.get("/documents/{doc_id}")
async def get_all_documents(doc_id: str):
    try:
        resp = await es.get(index=INDEX_NAME, id=doc_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Document not found")

    return resp["_source"]