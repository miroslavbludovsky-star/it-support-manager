"""JIRA email notification parser.

Parses emails from mailer@marbes.cz and extracts ticket data,
comments, and status changes.
"""

import re
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email import Email
from app.models.ticket import Ticket, TicketComment, TicketStatusChange

# Regex patterns for JIRA notification parsing
JIRA_KEY_RE = re.compile(r"Klíč:\s*([A-Z]+-[A-Z0-9]+-\d+)")
ISSUE_TYPE_RE = re.compile(r"Typ problému:\s*(.+?)(?:\s{2,}|$)")
STATUS_RE = re.compile(r"Stav:\s*(.+?)(?:\s{2,}|$)")
PRIORITY_RE = re.compile(r"Priorita:\s*(.+?)(?:\s{2,}|$)")
RESOLUTION_RE = re.compile(r"Rozhodnutí:\s*(.+?)(?:\s{2,}|$)")
ASSIGNEE_RE = re.compile(r"Přiřazený:\s*(.+?)(?:\s{2,}|$)")
REPORTER_RE = re.compile(r"Zadavatel:\s*(.+?)(?:\s{2,}|$)")
REMAINING_RE = re.compile(r"Zbývající odhad:\s*(.+?)(?:\s{2,}|$)")
TIME_SPENT_RE = re.compile(r"Odpracovaný čas:\s*(.+?)(?:\s{2,}|$)")
PROJECT_RE = re.compile(r"Projekt:\s*([A-Z]+-[A-Z0-9]+)\s*\((.+?)\)")
COMPONENTS_RE = re.compile(r"Komponenty:\s*(.+?)(?:\n|$)")
ATTACHMENTS_RE = re.compile(r"Attachments:\s*(.+?)(?:\n|$)")
TITLE_RE = re.compile(r"^(.+?)\s{3,}Aktualizovaný:", re.MULTILINE)
CREATED_RE = re.compile(r"Vytvořený:\s*(\d{2}\.\d{2}\.\d{2}\s+\d{1,2}:\d{2})")
UPDATED_RE = re.compile(r"Aktualizovaný:\s*(\d{2}\.\d{2}\.\d{2}\s+\d{1,2}:\d{2})")
COMMENT_RE = re.compile(
    r"(?:Author|Updater):\s*(.+?)\s+Date:\s*(.+?)\n\s*Komentář:\s*(.*?)(?=\n\s*Field|$)",
    re.DOTALL,
)
FIELD_CHANGE_RE = re.compile(
    r"(Stav|Priorita|Přiřazený)\s+(.+?)\s*\[\s*\d+\s*\]\s*(.+?)\s*\[\s*\d+\s*\]",
)
CHANGE_BY_RE = re.compile(r"Change By\s+(.+?)\s+on\s+(.+?)(?:\n|$)")

# Detection patterns
RESOLVED_RE = re.compile(r"resolved as (\w+)", re.IGNORECASE)
UPDATED_NOTICE_RE = re.compile(r"has been updated", re.IGNORECASE)
COMMENT_NOTICE_RE = re.compile(r"comment has been added", re.IGNORECASE)


def _parse_date(date_str: str) -> datetime | None:
    """Parse Czech-style date from JIRA notification."""
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ("%d.%m.%y %H:%M", "%d.%m.%Y %H:%M", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def _extract_customer_name(project_name: str) -> str:
    """Extract customer name from project name (text in parentheses or after dash)."""
    # Try to extract from parentheses first
    match = re.search(r"\((.+?)\)", project_name)
    if match:
        return match.group(1)
    # Otherwise use project name parts
    parts = project_name.split()
    if len(parts) > 2:
        return " ".join(parts[2:])
    return project_name


def _derive_waiting_on(status: str, assignee: str, reporter: str) -> str | None:
    """Auto-derive waiting_on based on ticket status."""
    status_lower = status.lower().strip()
    if "upřesnit" in status_lower:
        return reporter
    elif "v řešení" in status_lower or "řešení" in status_lower:
        return assignee
    elif "vyřešeno" in status_lower:
        return reporter
    return None


def _regex_extract(pattern: re.Pattern, text: str) -> str:
    """Extract first match group or return empty string."""
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def parse_jira_notification(body_text: str) -> dict | None:
    """Parse a JIRA email notification body and return structured data."""
    jira_key = _regex_extract(JIRA_KEY_RE, body_text)
    if not jira_key:
        return None

    # Extract project info
    project_match = PROJECT_RE.search(body_text)
    project_key = project_match.group(1) if project_match else jira_key.rsplit("-", 1)[0]
    project_name = project_match.group(2) if project_match else ""

    status = _regex_extract(STATUS_RE, body_text)
    assignee = _regex_extract(ASSIGNEE_RE, body_text)
    reporter = _regex_extract(REPORTER_RE, body_text)

    # Detect notification type
    resolution_match = RESOLVED_RE.search(body_text)
    resolution = _regex_extract(RESOLUTION_RE, body_text) or (
        resolution_match.group(1) if resolution_match else None
    )

    data = {
        "jira_key": jira_key,
        "project_key": project_key,
        "project_name": project_name,
        "customer_name": _extract_customer_name(project_name),
        "summary": _regex_extract(TITLE_RE, body_text),
        "issue_type": _regex_extract(ISSUE_TYPE_RE, body_text),
        "status": status,
        "priority": _regex_extract(PRIORITY_RE, body_text),
        "resolution": resolution,
        "assignee": assignee,
        "reporter": reporter,
        "components": _regex_extract(COMPONENTS_RE, body_text),
        "remaining_estimate": _regex_extract(REMAINING_RE, body_text),
        "time_spent": _regex_extract(TIME_SPENT_RE, body_text),
        "attachments": _regex_extract(ATTACHMENTS_RE, body_text) or None,
        "created_at": _parse_date(_regex_extract(CREATED_RE, body_text)),
        "updated_at": _parse_date(_regex_extract(UPDATED_RE, body_text)),
        "waiting_on": _derive_waiting_on(status, assignee, reporter),
    }

    # Extract comments
    comments = []
    for match in COMMENT_RE.finditer(body_text):
        comments.append({
            "author": match.group(1).strip(),
            "created_at": _parse_date(match.group(2).strip()),
            "body": match.group(3).strip(),
        })

    # Extract field changes
    changes = []
    change_by = _regex_extract(CHANGE_BY_RE, body_text)
    change_date_match = CHANGE_BY_RE.search(body_text)
    change_date = (
        _parse_date(change_date_match.group(2)) if change_date_match else None
    )
    for match in FIELD_CHANGE_RE.finditer(body_text):
        changes.append({
            "field": match.group(1).strip(),
            "old_value": match.group(2).strip(),
            "new_value": match.group(3).strip(),
            "changed_by": change_by,
            "changed_at": change_date,
        })

    # Extract description (after "Popis" heading)
    desc_match = re.search(r"Popis\s*\n(.+?)$", body_text, re.DOTALL)
    if desc_match:
        data["description"] = desc_match.group(1).strip()
    else:
        data["description"] = ""

    data["comments"] = comments
    data["status_changes"] = changes

    return data


async def process_jira_email(email: Email, db: AsyncSession) -> Ticket | None:
    """Process a JIRA notification email: parse and upsert ticket data."""
    parsed = parse_jira_notification(email.body_text)
    if not parsed:
        return None

    # Upsert ticket
    result = await db.execute(
        select(Ticket).where(Ticket.jira_key == parsed["jira_key"])
    )
    ticket = result.scalar_one_or_none()

    ticket_fields = {
        k: v
        for k, v in parsed.items()
        if k not in ("comments", "status_changes") and v is not None
    }

    if ticket:
        # Update existing - don't override manual waiting_on
        if ticket.waiting_on_manual:
            ticket_fields.pop("waiting_on", None)
        for key, value in ticket_fields.items():
            setattr(ticket, key, value)
        ticket.last_synced_at = datetime.utcnow()
    else:
        ticket = Ticket(**ticket_fields, last_synced_at=datetime.utcnow())
        db.add(ticket)

    await db.flush()

    # Add comments (deduplicate by source_email_id)
    for comment_data in parsed.get("comments", []):
        existing = await db.execute(
            select(TicketComment).where(
                TicketComment.ticket_id == ticket.id,
                TicketComment.source_email_id == email.ms_graph_id,
                TicketComment.author == comment_data["author"],
            )
        )
        if not existing.scalar_one_or_none():
            comment = TicketComment(
                ticket_id=ticket.id,
                author=comment_data["author"],
                body=comment_data["body"],
                created_at=comment_data.get("created_at"),
                source_email_id=email.ms_graph_id,
            )
            db.add(comment)

    # Add status changes
    for change_data in parsed.get("status_changes", []):
        existing = await db.execute(
            select(TicketStatusChange).where(
                TicketStatusChange.ticket_id == ticket.id,
                TicketStatusChange.source_email_id == email.ms_graph_id,
                TicketStatusChange.field == change_data["field"],
            )
        )
        if not existing.scalar_one_or_none():
            change = TicketStatusChange(
                ticket_id=ticket.id,
                field=change_data["field"],
                old_value=change_data["old_value"],
                new_value=change_data["new_value"],
                changed_by=change_data.get("changed_by", ""),
                changed_at=change_data.get("changed_at"),
                source_email_id=email.ms_graph_id,
            )
            db.add(change)

    # Link email to ticket
    email.linked_ticket_id = ticket.id
    email.is_processed = True
    await db.commit()

    return ticket
