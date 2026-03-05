from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.ticket import Ticket, TicketComment, TicketStatusChange
from app.schemas.ticket import (
    RelatedTicketResponse,
    TicketDetailResponse,
    TicketListResponse,
    TicketUpdateRequest,
)
from app.services.vector_store import find_related_tickets

router = APIRouter()


@router.get("/tickets", response_model=list[TicketListResponse])
async def list_tickets(
    project_key: str | None = None,
    customer_name: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    assignee: str | None = None,
    search: str | None = None,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Ticket).order_by(Ticket.updated_at.desc())

    if project_key:
        query = query.where(Ticket.project_key == project_key)
    if customer_name:
        query = query.where(Ticket.customer_name.ilike(f"%{customer_name}%"))
    if status:
        query = query.where(Ticket.status == status)
    if priority:
        query = query.where(Ticket.priority == priority)
    if assignee:
        query = query.where(Ticket.assignee.ilike(f"%{assignee}%"))
    if search:
        query = query.where(
            Ticket.summary.ilike(f"%{search}%") | Ticket.jira_key.ilike(f"%{search}%")
        )

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/tickets/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(selectinload(Ticket.comments), selectinload(Ticket.status_changes))
    )
    result = await db.execute(query)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/tickets/by-key/{jira_key}", response_model=TicketDetailResponse)
async def get_ticket_by_key(jira_key: str, db: AsyncSession = Depends(get_db)):
    query = (
        select(Ticket)
        .where(Ticket.jira_key == jira_key)
        .options(selectinload(Ticket.comments), selectinload(Ticket.status_changes))
    )
    result = await db.execute(query)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/tickets/{ticket_id}", response_model=TicketDetailResponse)
async def update_ticket(
    ticket_id: int,
    update: TicketUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(selectinload(Ticket.comments), selectinload(Ticket.status_changes))
    )
    result = await db.execute(query)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if update.waiting_on is not None:
        ticket.waiting_on = update.waiting_on
        ticket.waiting_on_manual = update.waiting_on_manual
    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.get("/tickets/{ticket_id}/related", response_model=list[RelatedTicketResponse])
async def get_related_tickets(
    ticket_id: int,
    limit: int = Query(default=5, le=20),
    db: AsyncSession = Depends(get_db),
):
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return await find_related_tickets(ticket, limit=limit, db=db)
