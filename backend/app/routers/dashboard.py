from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.email import Email, EmailCategory
from app.models.ticket import Ticket
from app.schemas.settings import DashboardSummary

router = APIRouter()


@router.get("/dashboard/summary", response_model=DashboardSummary)
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    # Ticket counts
    total = (await db.execute(select(func.count(Ticket.id)))).scalar() or 0
    open_q = select(func.count(Ticket.id)).where(Ticket.status != "Vyřešeno")
    open_count = (await db.execute(open_q)).scalar() or 0
    resolved = total - open_count

    # Waiting on
    waiting_me_q = select(func.count(Ticket.id)).where(
        Ticket.waiting_on.ilike("%assignee%") | Ticket.status.in_(["V řešení"])
    )
    waiting_me = (await db.execute(waiting_me_q)).scalar() or 0

    waiting_customer_q = select(func.count(Ticket.id)).where(
        Ticket.status.in_(["Upřesnit", "Vyřešeno"])
    )
    waiting_customer = (await db.execute(waiting_customer_q)).scalar() or 0

    # Email counts
    unread_q = select(func.count(Email.id)).where(
        Email.is_read == False, Email.category != EmailCategory.JIRA
    )
    unread = (await db.execute(unread_q)).scalar() or 0

    needs_resp_q = select(func.count(Email.id)).where(Email.needs_response == True)
    needs_resp = (await db.execute(needs_resp_q)).scalar() or 0

    # Tickets by project
    proj_q = select(Ticket.project_name, func.count(Ticket.id)).group_by(
        Ticket.project_name
    )
    proj_result = (await db.execute(proj_q)).all()
    by_project = {row[0]: row[1] for row in proj_result if row[0]}

    # Tickets by status
    status_q = select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status)
    status_result = (await db.execute(status_q)).all()
    by_status = {row[0]: row[1] for row in status_result if row[0]}

    # Recent tickets
    recent_q = select(Ticket).order_by(Ticket.updated_at.desc()).limit(10)
    recent_result = (await db.execute(recent_q)).scalars().all()
    recent = [
        {
            "jira_key": t.jira_key,
            "summary": t.summary,
            "status": t.status,
            "priority": t.priority,
            "assignee": t.assignee,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        }
        for t in recent_result
    ]

    return DashboardSummary(
        total_tickets=total,
        open_tickets=open_count,
        resolved_tickets=resolved,
        waiting_on_me=waiting_me,
        waiting_on_customer=waiting_customer,
        unread_emails=unread,
        emails_needing_response=needs_resp,
        tickets_by_project=by_project,
        tickets_by_status=by_status,
        recent_tickets=recent,
    )
