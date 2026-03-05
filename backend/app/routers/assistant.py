from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.settings import AssistantChatRequest, AssistantChatResponse
from app.services.ai_assistant import chat_with_assistant

router = APIRouter()


@router.post("/assistant/chat", response_model=AssistantChatResponse)
async def assistant_chat(
    request: AssistantChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """AI Assistant - RAG-based chat over tickets and emails."""
    result = await chat_with_assistant(
        message=request.message,
        ticket_context_id=request.ticket_context_id,
        db=db,
    )
    return result
