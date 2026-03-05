"""LLM service for generating email draft responses using Ollama."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.email import Email, EmailCategory
from app.models.settings import AppSettings

logger = logging.getLogger(__name__)

DEFAULT_PROMPT = (
    "Jsi asistent projektového manažera v IT firmě Marbes. Píšeš profesionální emaily\n"
    "v češtině. Tvůj styl komunikace je inspirovaný Chris Vossem (Never Split the\n"
    "Difference) - používáš taktickou empatii, zrcadlení, otevřené kalibrované otázky\n"
    "a pozitivní formulace. Jsi diplomatický, empatický, ale asertivní.\n\n"
    "Pravidla:\n"
    "- Piš stručně a věcně, ale vřele a lidsky\n"
    "- Vždy používej oslovení a pozdrav\n"
    "- Nikdy neslibuj konkrétní termíny, pokud nemáš data\n"
    "- Pokud jde o technický problém, potvrzuj porozumění a nabízej další kroky\n"
    "- U interních mailů buď méně formální než u externích\n"
    '- Používej "Jak bych vám mohl nejlépe pomoci?" místo "Co potřebujete?"\n'
    '- Pojmenovávej emoce protistrany: "Zdá se, že vás to frustruje..."\n'
    '- Používej pozdrav "S pozdravem" nebo "S úctou" podle formality'
)


async def _get_llm_prompt(db: AsyncSession) -> str:
    """Get LLM prompt from settings or use default."""
    result = await db.execute(
        select(AppSettings).where(AppSettings.key == "llm_prompt")
    )
    setting = result.scalar_one_or_none()
    return setting.value if setting else DEFAULT_PROMPT


async def generate_email_draft(
    email: Email, db: AsyncSession
) -> tuple[str, str]:
    """Generate a draft response for an email using Ollama.

    Returns (draft_body, prompt_used).
    """
    settings = get_settings()
    system_prompt = await _get_llm_prompt(db)

    formality = "formální" if email.category == EmailCategory.EXTERNAL else "neformální"
    user_prompt = (
        f"Napiš {formality} odpověď na tento email:\n\n"
        f"Od: {email.sender_name} <{email.sender_email}>\n"
        f"Předmět: {email.subject}\n\n"
        f"{email.body_text}\n\n"
        f"Napiš pouze text odpovědi, bez předmětu."
    )

    try:
        from langchain_ollama import ChatOllama

        llm = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_host,
        )

        messages = [
            ("system", system_prompt),
            ("human", user_prompt),
        ]

        response = await llm.ainvoke(messages)
        return response.content, system_prompt

    except Exception as e:
        logger.exception("LLM draft generation failed")
        return (
            f"[Chyba při generování odpovědi: {e}]\n\n"
            "Zkontrolujte, zda je Ollama dostupná a model stažen.",
            system_prompt,
        )
