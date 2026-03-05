"""MS Graph email sync service.

Polls O365 mailbox via MS Graph API and stores emails in the database.
"""

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import async_session
from app.models.email import Email, EmailCategory
from app.services.email_classifier import classify_email
from app.services.jira_parser import process_jira_email

logger = logging.getLogger(__name__)


async def _get_graph_client():
    """Create MS Graph client using Azure credentials."""
    settings = get_settings()
    if not all([settings.azure_tenant_id, settings.azure_client_id, settings.azure_client_secret]):
        raise RuntimeError("Azure credentials not configured")

    from azure.identity.aio import ClientSecretCredential
    from msgraph import GraphServiceClient

    credential = ClientSecretCredential(
        tenant_id=settings.azure_tenant_id,
        client_id=settings.azure_client_id,
        client_secret=settings.azure_client_secret,
    )
    return GraphServiceClient(credential), credential


async def _fetch_emails_from_graph(since: datetime | None = None) -> list[dict]:
    """Fetch emails from MS Graph API."""
    settings = get_settings()
    client, credential = await _get_graph_client()

    try:
        filter_str = ""
        if since:
            filter_str = f"receivedDateTime gt {since.strftime('%Y-%m-%dT%H:%M:%SZ')}"

        messages = (
            await client.users.by_user_id(settings.mailbox_user_email)
            .messages.get(
                request_configuration=lambda config: setattr(
                    config.query_parameters, "filter", filter_str
                )
                or setattr(config.query_parameters, "orderby", ["receivedDateTime asc"])
                or setattr(config.query_parameters, "top", 50)
            )
        )

        results = []
        if messages and messages.value:
            for msg in messages.value:
                results.append({
                    "ms_graph_id": msg.id,
                    "subject": msg.subject or "",
                    "sender_email": (
                        msg.from_.email_address.address
                        if msg.from_ and msg.from_.email_address
                        else ""
                    ),
                    "sender_name": (
                        msg.from_.email_address.name
                        if msg.from_ and msg.from_.email_address
                        else ""
                    ),
                    "received_at": msg.received_date_time,
                    "body_text": msg.body.content if msg.body else "",
                    "body_html": msg.body.content if msg.body else "",
                })
        return results
    finally:
        await credential.close()


async def sync_emails(db: AsyncSession | None = None) -> int:
    """Sync emails from O365 mailbox. Returns count of new emails."""
    settings = get_settings()

    if settings.dev_mode:
        logger.info("Dev mode: skipping email sync")
        return 0

    own_session = db is None
    if own_session:
        session = async_session()
    else:
        session = db

    try:
        # Get last sync time
        last_email = await session.execute(
            select(Email).order_by(Email.received_at.desc()).limit(1)
        )
        last = last_email.scalar_one_or_none()
        since = last.received_at if last else None

        # Fetch from Graph
        raw_emails = await _fetch_emails_from_graph(since=since)
        count = 0

        for raw in raw_emails:
            # Deduplicate
            existing = await session.execute(
                select(Email).where(Email.ms_graph_id == raw["ms_graph_id"])
            )
            if existing.scalar_one_or_none():
                continue

            category = classify_email(raw["sender_email"], raw["body_text"])
            email = Email(
                ms_graph_id=raw["ms_graph_id"],
                subject=raw["subject"],
                sender_email=raw["sender_email"],
                sender_name=raw["sender_name"],
                received_at=raw["received_at"],
                body_text=raw["body_text"],
                body_html=raw["body_html"],
                category=category,
                needs_response=category != EmailCategory.JIRA,
            )
            session.add(email)
            await session.flush()

            # Process JIRA emails
            if category == EmailCategory.JIRA:
                await process_jira_email(email, session)

            count += 1

        if own_session:
            await session.commit()
        else:
            await session.commit()

        logger.info(f"Synced {count} new emails")
        return count

    except Exception:
        logger.exception("Email sync failed")
        if own_session:
            await session.rollback()
        raise
    finally:
        if own_session:
            await session.close()
