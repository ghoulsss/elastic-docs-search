from elasticsearch import AsyncElasticsearch

from config import ELASTIC_HOST, INDEX_NAME

es = AsyncElasticsearch(hosts=[ELASTIC_HOST])


async def create_index():
    exists = await es.indices.exists(index=INDEX_NAME)
    if not exists:
        await es.indices.create(
            index=INDEX_NAME,
            mappings={
                "properties": {
                    "documentId": {"type": "keyword"},
                    "pages": {
                        "type": "nested",
                        "properties": {
                            "pageNum": {"type": "integer"},
                            "pageSummary": {
                                "type": "text",
                                "fields": {
                                    "raw": {  # ← ТОЧНОЕ совпадение
                                        "type": "keyword",
                                        "normalizer": "lowercase_normalizer",
                                    }
                                },
                            },
                        },
                    },
                }
            },
            settings={
                "analysis": {
                    "normalizer": {
                        "lowercase_normalizer": {
                            "type": "custom",
                            "filter": ["lowercase"],
                        }
                    }
                }
            },
        )


async def index_document(document):
    """
    document = {
        "documentId": "...",
        "pages": [{"pageNum": 1, "pageSummary": "text"}, ...]
    }
    """
    await es.index(index=INDEX_NAME, id=document["documentId"], document=document)


async def close():
    await es.close()


async def delete_index():
    exists = await es.indices.exists(index=INDEX_NAME)
    if not exists:
        return {"status": "error", "message": "Index does not exist"}

    await es.indices.delete(index=INDEX_NAME)
    return {"status": "ok", "message": "Index deleted"}
