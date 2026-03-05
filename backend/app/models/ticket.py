from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    jira_key: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    project_key: Mapped[str] = mapped_column(String(50), index=True)
    project_name: Mapped[str] = mapped_column(String(255), default="")
    customer_name: Mapped[str] = mapped_column(String(255), default="")
    summary: Mapped[str] = mapped_column(String(500), default="")
    issue_type: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(100), default="")
    priority: Mapped[str] = mapped_column(String(50), default="")
    resolution: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assignee: Mapped[str] = mapped_column(String(255), default="")
    reporter: Mapped[str] = mapped_column(String(255), default="")
    components: Mapped[str] = mapped_column(String(500), default="")
    remaining_estimate: Mapped[str] = mapped_column(String(50), default="")
    time_spent: Mapped[str] = mapped_column(String(50), default="")
    waiting_on: Mapped[str | None] = mapped_column(String(255), nullable=True)
    waiting_on_manual: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(Text, default="")
    attachments: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    comments: Mapped[list["TicketComment"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
    status_changes: Mapped[list["TicketStatusChange"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    author: Mapped[str] = mapped_column(String(255), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_email_id: Mapped[str] = mapped_column(String(255), default="", index=True)

    ticket: Mapped["Ticket"] = relationship(back_populates="comments")


class TicketStatusChange(Base):
    __tablename__ = "ticket_status_changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    field: Mapped[str] = mapped_column(String(100), default="")
    old_value: Mapped[str] = mapped_column(String(255), default="")
    new_value: Mapped[str] = mapped_column(String(255), default="")
    changed_by: Mapped[str] = mapped_column(String(255), default="")
    changed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_email_id: Mapped[str] = mapped_column(String(255), default="", index=True)

    ticket: Mapped["Ticket"] = relationship(back_populates="status_changes")
