import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.email import Email, EmailCategory, EmailDraft
from app.schemas.email import (
    DevInjectEmailRequest,
    EmailDetailResponse,
    EmailDraftResponse,
    EmailListResponse,
)
from app.services.email_classifier import classify_email
from app.services.jira_parser import process_jira_email
from app.services.llm_service import generate_email_draft

router = APIRouter()


@router.get("/emails", response_model=list[EmailListResponse])
async def list_emails(
    category: str | None = None,
    needs_response: bool | None = None,
    is_read: bool | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Email).order_by(Email.received_at.desc())

    if category:
        query = query.where(Email.category == category)
    if needs_response is not None:
        query = query.where(Email.needs_response == needs_response)
    if is_read is not None:
        query = query.where(Email.is_read == is_read)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/emails/{email_id}", response_model=EmailDetailResponse)
async def get_email(email_id: int, db: AsyncSession = Depends(get_db)):
    email = await db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    # Mark as read
    email.is_read = True
    await db.commit()
    return email


@router.post("/emails/{email_id}/draft", response_model=EmailDraftResponse)
async def create_draft(email_id: int, db: AsyncSession = Depends(get_db)):
    email = await db.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    draft_body, prompt_used = await generate_email_draft(email, db=db)
    draft = EmailDraft(
        email_id=email.id,
        draft_body=draft_body,
        prompt_used=prompt_used,
        created_at=datetime.utcnow(),
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)
    return draft


@router.post("/dev/inject-email", response_model=EmailListResponse)
async def dev_inject_email(
    request: DevInjectEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    """Dev mode: inject a test email for parser testing."""
    category = classify_email(request.sender_email, request.body_text)

    email = Email(
        ms_graph_id=f"dev-{uuid.uuid4()}",
        subject=request.subject,
        sender_email=request.sender_email,
        sender_name=request.sender_name,
        received_at=datetime.utcnow(),
        body_text=request.body_text,
        body_html=request.body_html,
        category=category,
        needs_response=category != EmailCategory.JIRA,
    )
    db.add(email)
    await db.commit()
    await db.refresh(email)

    if category == EmailCategory.JIRA:
        await process_jira_email(email, db)

    return email
