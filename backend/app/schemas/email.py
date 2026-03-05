from datetime import datetime

from pydantic import BaseModel


class EmailListResponse(BaseModel):
    id: int
    ms_graph_id: str
    subject: str
    sender_email: str
    sender_name: str
    received_at: datetime | None
    category: str
    is_processed: bool
    is_read: bool
    needs_response: bool
    linked_ticket_id: int | None

    model_config = {"from_attributes": True}


class EmailDetailResponse(EmailListResponse):
    body_text: str
    body_html: str


class EmailDraftResponse(BaseModel):
    id: int
    email_id: int
    draft_body: str
    prompt_used: str
    created_at: datetime
    is_approved: bool

    model_config = {"from_attributes": True}


class DevInjectEmailRequest(BaseModel):
    subject: str
    sender_email: str
    sender_name: str = ""
    body_text: str
    body_html: str = ""
