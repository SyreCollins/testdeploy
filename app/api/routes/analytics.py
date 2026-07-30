from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from sqlmodel import Session, func, select

from app.core.config import get_settings
from app.db.engine import get_engine
from app.db.models.usage import UsageRecord

router = APIRouter(prefix="/v1/organizations/me/analytics", tags=["analytics"])


def _get_org_id(request: Request) -> int:
    org_id = getattr(request.state, "org_id", None) or getattr(request.state, "organization_id", None)
    if org_id is None:
        raise HTTPException(status_code=401, detail="Organization not identified")
    return org_id


class SummaryResponse(BaseModel):
    organization_id: int
    total_requests: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    unique_endpoints: int = 0
    daily_avg_requests: float = 0
    period_days: int = 0
    from_date: str
    to_date: str


class TrendPoint(BaseModel):
    date: str
    requests: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0


class TrendsResponse(BaseModel):
    organization_id: int
    from_date: str
    to_date: str
    trends: list[TrendPoint]


class TopEndpoint(BaseModel):
    endpoint: str
    request_count: int = 0
    percentage: float = 0


class TopEndpointsResponse(BaseModel):
    organization_id: int
    from_date: str
    to_date: str
    endpoints: list[TopEndpoint]


@router.get("/summary")
def get_summary(
    request: Request,
    from_date: str = Query(default=None, alias="from"),
    to_date: str = Query(default=None, alias="to"),
) -> SummaryResponse:
    org_id = _get_org_id(request)
    if not to_date:
        to_date = datetime.now(UTC).strftime("%Y-%m-%d")
    if not from_date:
        from_date = (datetime.now(UTC) - timedelta(days=30)).strftime("%Y-%m-%d")

    with Session(get_engine(get_settings().database_url)) as session:
        query = select(
            func.sum(UsageRecord.request_count),
            func.sum(UsageRecord.prompt_tokens),
            func.sum(UsageRecord.completion_tokens),
            func.count(func.distinct(UsageRecord.endpoint)),
        ).where(
            UsageRecord.organization_id == org_id,
            UsageRecord.date >= from_date,
            UsageRecord.date <= to_date,
        )
        row = session.exec(query).one()
        total_requests = row[0] or 0
        total_prompt = row[1] or 0
        total_completion = row[2] or 0
        unique_eps = row[3] or 0

    from_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    period_days = max(1, (to_dt - from_dt).days + 1)

    return SummaryResponse(
        organization_id=org_id,
        total_requests=total_requests,
        total_prompt_tokens=total_prompt,
        total_completion_tokens=total_completion,
        unique_endpoints=unique_eps,
        daily_avg_requests=round(total_requests / period_days, 1),
        period_days=period_days,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/trends")
def get_trends(
    request: Request,
    from_date: str = Query(default=None, alias="from"),
    to_date: str = Query(default=None, alias="to"),
) -> TrendsResponse:
    org_id = _get_org_id(request)
    if not to_date:
        to_date = datetime.now(UTC).strftime("%Y-%m-%d")
    if not from_date:
        from_date = (datetime.now(UTC) - timedelta(days=30)).strftime("%Y-%m-%d")

    with Session(get_engine(get_settings().database_url)) as session:
        query = select(
            UsageRecord.date,
            func.sum(UsageRecord.request_count),
            func.sum(UsageRecord.prompt_tokens),
            func.sum(UsageRecord.completion_tokens),
        ).where(
            UsageRecord.organization_id == org_id,
            UsageRecord.date >= from_date,
            UsageRecord.date <= to_date,
        ).group_by(UsageRecord.date).order_by(UsageRecord.date)
        rows = session.exec(query).all()

    from_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_dt = datetime.strptime(to_date, "%Y-%m-%d")
    date_set = {r[0] for r in rows}

    trends = []
    current = from_dt
    while current <= to_dt:
        date_str = current.strftime("%Y-%m-%d")
        if date_str in date_set:
            row = next(r for r in rows if r[0] == date_str)
            trends.append(TrendPoint(
                date=date_str,
                requests=row[1] or 0,
                prompt_tokens=row[2] or 0,
                completion_tokens=row[3] or 0,
            ))
        else:
            trends.append(TrendPoint(date=date_str))
        current += timedelta(days=1)

    return TrendsResponse(
        organization_id=org_id,
        from_date=from_date,
        to_date=to_date,
        trends=trends,
    )


@router.get("/top-endpoints")
def get_top_endpoints(
    request: Request,
    from_date: str = Query(default=None, alias="from"),
    to_date: str = Query(default=None, alias="to"),
    limit: int = Query(default=10, le=50),
) -> TopEndpointsResponse:
    org_id = _get_org_id(request)
    if not to_date:
        to_date = datetime.now(UTC).strftime("%Y-%m-%d")
    if not from_date:
        from_date = (datetime.now(UTC) - timedelta(days=30)).strftime("%Y-%m-%d")

    with Session(get_engine(get_settings().database_url)) as session:
        query = select(
            UsageRecord.endpoint,
            func.sum(UsageRecord.request_count),
        ).where(
            UsageRecord.organization_id == org_id,
            UsageRecord.date >= from_date,
            UsageRecord.date <= to_date,
        ).group_by(UsageRecord.endpoint).order_by(func.sum(UsageRecord.request_count).desc()).limit(limit)
        rows = session.exec(query).all()

    total = sum(row[1] or 0 for row in rows) or 1
    endpoints = [
        TopEndpoint(endpoint=row[0], request_count=row[1] or 0, percentage=round((row[1] or 0) / total * 100, 1))
        for row in rows
    ]

    return TopEndpointsResponse(
        organization_id=org_id,
        from_date=from_date,
        to_date=to_date,
        endpoints=endpoints,
    )
