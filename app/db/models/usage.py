from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class UsageRecord(SQLModel, table=True):
    __tablename__ = "usage_records"

    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organizations.id", index=True)
    api_key_id: str | None = None
    date: str
    endpoint: str
    request_count: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UsageDailyTotals(SQLModel, table=True):
    __tablename__ = "usage_daily_totals"

    id: int | None = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organizations.id", index=True)
    date: str
    total_requests: int
    total_prompt_tokens: int
    total_completion_tokens: int
    unique_endpoints: int
