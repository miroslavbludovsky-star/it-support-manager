"""ChromaDB vector store for ticket semantic search."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.ticket import Ticket

logger = logging.getLogger(__name__)

_collection = None
_client = None


async def init_vector_store():
    """Initialize ChromaDB client and collection."""
    global _client, _collection
    try:
        import chromadb

        settings = get_settings()
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        _collection = _client.get_or_create_collection(
            name="tickets",
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("ChromaDB initialized")
    except Exception:
        logger.warning("ChromaDB initialization failed - vector search unavailable")


def _get_collection():
    if _collection is None:
        raise RuntimeError("Vector store not initialized")
    return _collection


async def index_ticket(ticket: Ticket):
    """Index a ticket in ChromaDB."""
    try:
        collection = _get_collection()
        doc_text = f"{ticket.jira_key}: {ticket.summary}\n{ticket.description}"
        collection.upsert(
            ids=[ticket.jira_key],
            documents=[doc_text],
            metadatas=[{
                "jira_key": ticket.jira_key,
                "project_key": ticket.project_key,
                "status": ticket.status,
                "assignee": ticket.assignee,
            }],
        )
    except Exception:
        logger.warning(f"Failed to index ticket {ticket.jira_key}")


async def index_all_tickets(db: AsyncSession):
    """Re-index all tickets."""
    result = await db.execute(select(Ticket))
    tickets = result.scalars().all()
    for ticket in tickets:
        await index_ticket(ticket)
    logger.info(f"Indexed {len(tickets)} tickets in ChromaDB")


async def search_tickets(query: str, n_results: int = 10) -> list[dict]:
    """Semantic search over tickets."""
    try:
        collection = _get_collection()
        results = collection.query(query_texts=[query], n_results=n_results)

        found = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                found.append({
                    "jira_key": doc_id,
                    "document": results["documents"][0][i] if results["documents"] else "",
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                })
        return found
    except Exception:
        logger.warning("Vector search failed")
        return []


async def find_related_tickets(
    ticket: Ticket, limit: int = 5, db: AsyncSession = None
) -> list[dict]:
    """Find tickets related to the given ticket."""
    query = f"{ticket.summary} {ticket.description[:500]}"
    results = await search_tickets(query, n_results=limit + 1)

    # Exclude the ticket itself
    related = []
    for r in results:
        if r["jira_key"] != ticket.jira_key:
            related.append({
                "jira_key": r["jira_key"],
                "summary": r["document"].split("\n")[0] if r["document"] else "",
                "similarity": round(1 - r["distance"], 3) if r["distance"] else 0,
            })
    return related[:limit]
