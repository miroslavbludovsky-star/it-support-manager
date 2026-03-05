import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EmailCategory(str, enum.Enum):
    JIRA = "jira"
    INTERNAL = "internal"
    EXTERNAL = "external"


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ms_graph_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    subject: Mapped[str] = mapped_column(String(500), default="")
    sender_email: Mapped[str] = mapped_column(String(255), default="")
    sender_name: Mapped[str] = mapped_column(String(255), default="")
    received_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    body_text: Mapped[str] = mapped_column(Text, default="")
    body_html: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[EmailCategory] = mapped_column(
        Enum(EmailCategory), default=EmailCategory.EXTERNAL
    )
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    needs_response: Mapped[bool] = mapped_column(Boolean, default=False)
    linked_ticket_id: Mapped[int | None] = mapped_column(
        ForeignKey("tickets.id"), nullable=True
    )

    drafts: Mapped[list["EmailDraft"]] = relationship(
        back_populates="email", cascade="all, delete-orphan"
    )


class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_id: Mapped[int] = mapped_column(ForeignKey("emails.id"), index=True)
    draft_body: Mapped[str] = mapped_column(Text, default="")
    prompt_used: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)

    email: Mapped["Email"] = relationship(back_populates="drafts")
