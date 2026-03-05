from pydantic import BaseModel


class SettingResponse(BaseModel):
    key: str
    value: str

    model_config = {"from_attributes": True}


class SettingUpdateRequest(BaseModel):
    value: str


class DashboardSummary(BaseModel):
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    waiting_on_me: int
    waiting_on_customer: int
    unread_emails: int
    emails_needing_response: int
    tickets_by_project: dict[str, int]
    tickets_by_status: dict[str, int]
    recent_tickets: list[dict]


class AssistantChatRequest(BaseModel):
    message: str
    ticket_context_id: str | None = None


class AssistantChatResponse(BaseModel):
    answer: str
    related_tickets: list[str] = []
    sources: list[dict] = []
