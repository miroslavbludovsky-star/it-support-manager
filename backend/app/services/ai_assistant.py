"""AI Assistant - RAG over tickets using ChromaDB + Ollama."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.ticket import Ticket
from app.services.vector_store import search_tickets

logger = logging.getLogger(__name__)

ASSISTANT_SYSTEM_PROMPT = (
    "Jsi AI asistent projektového manažera v IT firmě Marbes. "
    "Máš přístup k databázi JIRA ticketů a pomáháš s:\n"
    "- Hledáním informací o ticketech\n"
    "- Nalézáním souvisejících ticketů a historických precedentů\n"
    "- Analýzou stavu projektů\n"
    "- Doporučeními na základě historie\n\n"
    "Odpovídej v češtině, stručně a věcně. "
    "Vždy uváděj konkrétní klíče ticketů (např. UDR-MMMB-2626) jako reference."
)


async def chat_with_assistant(
    message: str,
    ticket_context_id: str | None = None,
    db: AsyncSession = None,
) -> dict:
    """Process a chat message using RAG over tickets."""
    settings = get_settings()

    # Search for relevant tickets
    search_results = await search_tickets(message, n_results=5)

    # If specific ticket context provided, fetch it
    context_parts = []
    related_keys = []

    if ticket_context_id:
        result = await db.execute(
            select(Ticket).where(Ticket.jira_key == ticket_context_id)
        )
        ticket = result.scalar_one_or_none()
        if ticket:
            context_parts.append(
                f"Kontext ticketu {ticket.jira_key}:\n"
                f"- Název: {ticket.summary}\n"
                f"- Stav: {ticket.status}\n"
                f"- Priorita: {ticket.priority}\n"
                f"- Přiřazený: {ticket.assignee}\n"
                f"- Zadavatel: {ticket.reporter}\n"
                f"- Projekt: {ticket.project_name}\n"
                f"- Popis: {ticket.description[:1000]}"
            )

    # Add search results as context
    for r in search_results:
        jira_key = r["jira_key"]
        if jira_key not in related_keys:
            related_keys.append(jira_key)
        context_parts.append(f"Ticket {jira_key}: {r['document'][:500]}")

    context = "\n\n".join(context_parts)

    try:
        from langchain_ollama import ChatOllama

        llm = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_host,
        )

        user_msg = (
            f"Relevantní tickety z databáze:\n{context}\n\n"
            f"Dotaz uživatele: {message}"
        )

        messages = [
            ("system", ASSISTANT_SYSTEM_PROMPT),
            ("human", user_msg),
        ]

        response = await llm.ainvoke(messages)

        return {
            "answer": response.content,
            "related_tickets": related_keys,
            "sources": [
                {"jira_key": r["jira_key"], "distance": r.get("distance", 0)}
                for r in search_results
            ],
        }

    except Exception as e:
        logger.exception("AI Assistant failed")
        return {
            "answer": (
                f"Omlouvám se, nepodařilo se zpracovat dotaz: {e}\n"
                "Zkontrolujte, zda je Ollama dostupná."
            ),
            "related_tickets": related_keys,
            "sources": [],
        }
