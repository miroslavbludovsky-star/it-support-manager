from datetime import datetime

from pydantic import BaseModel


class TicketCommentResponse(BaseModel):
    id: int
    author: str
    body: str
    created_at: datetime | None

    model_config = {"from_attributes": True}


class TicketStatusChangeResponse(BaseModel):
    id: int
    field: str
    old_value: str
    new_value: str
    changed_by: str
    changed_at: datetime | None

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    id: int
    jira_key: str
    project_key: str
    project_name: str
    customer_name: str
    summary: str
    issue_type: str
    status: str
    priority: str
    resolution: str | None
    assignee: str
    reporter: str
    waiting_on: str | None
    waiting_on_manual: bool
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class TicketDetailResponse(TicketListResponse):
    components: str
    remaining_estimate: str
    time_spent: str
    description: str
    attachments: str | None
    created_at: datetime | None
    last_synced_at: datetime
    comments: list[TicketCommentResponse] = []
    status_changes: list[TicketStatusChangeResponse] = []


class TicketUpdateRequest(BaseModel):
    waiting_on: str | None = None
    waiting_on_manual: bool = True


class RelatedTicketResponse(BaseModel):
    jira_key: str
    summary: str
    similarity: float
