from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from sqlmodel import Session, func, select
from starlette import status

from app.api.schemas.audit import (
    AuditEventSummary,
    AuditTraceInfo,
    GetAuditTraceResponse,
    ListAuditTracesResponse,
)
from app.core.config import get_settings
from app.db.engine import get_engine
from app.db.models.platform import Organization, Project, User
from app.db.models.usage import UsageRecord

router = APIRouter(prefix="/v1/admin", tags=["admin"])


def _require_admin(request: Request) -> None:
    if not getattr(request.state, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


def _get_session():
    engine = get_engine(get_settings().database_url)
    with Session(engine) as session:
        yield session


class OrgSummary(BaseModel):
    id: int
    clerk_org_id: str
    name: str
    slug: str
    plan: str
    is_active: bool
    created_at: datetime
    member_count: int = 0
    project_count: int = 0


class UserSummary(BaseModel):
    id: int
    clerk_user_id: str
    email: str
    name: str | None = None
    role: str
    organization_id: int
    created_at: datetime


class ProjectSummary(BaseModel):
    id: int
    name: str
    slug: str
    environment: str
    organization_id: int
    created_at: datetime


class UsageSummary(BaseModel):
    organization_id: int
    date: str
    total_requests: int
    total_prompt_tokens: int
    total_completion_tokens: int
    unique_endpoints: int


class ListOrgsResponse(BaseModel):
    orgs: list[OrgSummary]
    total: int


class ListUsersResponse(BaseModel):
    users: list[UserSummary]
    total: int


class ListProjectsResponse(BaseModel):
    projects: list[ProjectSummary]
    total: int


class ListUsageResponse(BaseModel):
    records: list[UsageSummary]
    total: int


@router.get("/orgs", response_model=ListOrgsResponse)
def list_orgs(request: Request) -> ListOrgsResponse:
    _require_admin(request)
    with Session(get_engine(get_settings().database_url)) as session:
        orgs = session.exec(select(Organization).order_by(Organization.id)).all()
        items = []
        for org in orgs:
            member_count = session.exec(
                select(User).where(User.organization_id == org.id)
            ).all()
            project_count = session.exec(
                select(Project).where(Project.organization_id == org.id)
            ).all()
            items.append(OrgSummary(
                id=org.id,
                clerk_org_id=org.clerk_org_id,
                name=org.name,
                slug=org.slug,
                plan=org.plan,
                is_active=org.is_active,
                created_at=org.created_at,
                member_count=len(member_count),
                project_count=len(project_count),
            ))
        return ListOrgsResponse(orgs=items, total=len(items))


@router.get("/orgs/{org_id}", response_model=OrgSummary)
def get_org(request: Request, org_id: int) -> OrgSummary:
    _require_admin(request)
    with Session(get_engine(get_settings().database_url)) as session:
        org = session.get(Organization, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Organization not found")
        member_count = len(session.exec(
            select(User).where(User.organization_id == org.id)
        ).all())
        project_count = len(session.exec(
            select(Project).where(Project.organization_id == org.id)
        ).all())
        return OrgSummary(
            id=org.id,
            clerk_org_id=org.clerk_org_id,
            name=org.name,
            slug=org.slug,
            plan=org.plan,
            is_active=org.is_active,
            created_at=org.created_at,
            member_count=member_count,
            project_count=project_count,
        )


@router.get("/orgs/{org_id}/users", response_model=ListUsersResponse)
def list_org_users(request: Request, org_id: int) -> ListUsersResponse:
    _require_admin(request)
    with Session(get_engine(get_settings().database_url)) as session:
        org = session.get(Organization, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Organization not found")
        users = session.exec(
            select(User).where(User.organization_id == org_id).order_by(User.id)
        ).all()
        return ListUsersResponse(
            users=[UserSummary(
                id=u.id,
                clerk_user_id=u.clerk_user_id,
                email=u.email,
                name=u.name,
                role=u.role,
                organization_id=u.organization_id,
                created_at=u.created_at,
            ) for u in users],
            total=len(users),
        )


@router.get("/orgs/{org_id}/projects", response_model=ListProjectsResponse)
def list_org_projects(request: Request, org_id: int) -> ListProjectsResponse:
    _require_admin(request)
    with Session(get_engine(get_settings().database_url)) as session:
        org = session.get(Organization, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Organization not found")
        projects = session.exec(
            select(Project).where(Project.organization_id == org_id).order_by(Project.id)
        ).all()
        return ListProjectsResponse(
            projects=[ProjectSummary(
                id=p.id,
                name=p.name,
                slug=p.slug,
                environment=p.environment,
                organization_id=p.organization_id,
                created_at=p.created_at,
            ) for p in projects],
            total=len(projects),
        )


@router.get("/users", response_model=ListUsersResponse)
def list_users(
    request: Request,
    organization_id: int | None = Query(default=None, alias="org_id"),
) -> ListUsersResponse:
    _require_admin(request)
    with Session(get_engine(get_settings().database_url)) as session:
        query = select(User).order_by(User.id)
        if organization_id is not None:
            query = query.where(User.organization_id == organization_id)
        users = session.exec(query).all()
        return ListUsersResponse(
            users=[UserSummary(
                id=u.id,
                clerk_user_id=u.clerk_user_id,
                email=u.email,
                name=u.name,
                role=u.role,
                organization_id=u.organization_id,
                created_at=u.created_at,
            ) for u in users],
            total=len(users),
        )


@router.get("/audit/traces", response_model=ListAuditTracesResponse)
def list_audit_traces(
    request: Request,
    limit: int = Query(default=50, le=500),
    organization_id: int | None = Query(default=None, alias="org_id"),
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
) -> ListAuditTracesResponse:
    _require_admin(request)
    writer = request.app.state.audit_writer
    traces = writer.get_recent_traces(
        limit=limit,
        organization_id=organization_id,
        from_date=from_date,
        to_date=to_date,
    )
    return ListAuditTracesResponse(
        traces=[
            AuditTraceInfo(
                trace_id=t.trace_id,
                workflow=t.workflow,
                started_at=t.started_at,
                completed_at=t.completed_at,
                event_count=len(t.events),
                events=[
                    AuditEventSummary(
                        event_type=e.event_type,
                        timestamp=e.timestamp,
                        data=e.data,
                    )
                    for e in t.events
                ],
            )
            for t in traces
        ],
        total=len(traces),
    )


@router.get("/audit/traces/{trace_id}", response_model=GetAuditTraceResponse)
def get_audit_trace(request: Request, trace_id: str) -> GetAuditTraceResponse:
    _require_admin(request)
    writer = request.app.state.audit_writer
    trace = writer.get_trace(trace_id)
    if trace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found")
    return GetAuditTraceResponse(
        trace=AuditTraceInfo(
            trace_id=trace.trace_id,
            workflow=trace.workflow,
            started_at=trace.started_at,
            completed_at=trace.completed_at,
            event_count=len(trace.events),
            events=[
                AuditEventSummary(
                    event_type=e.event_type,
                    timestamp=e.timestamp,
                    data=e.data,
                )
                for e in trace.events
            ],
        )
    )


@router.get("/usage", response_model=ListUsageResponse)
def list_usage(
    request: Request,
    organization_id: int | None = Query(default=None, alias="org_id"),
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
) -> ListUsageResponse:
    _require_admin(request)
    with Session(get_engine(get_settings().database_url)) as session:
        query = select(
            UsageRecord.organization_id,
            UsageRecord.date,
            func.sum(UsageRecord.request_count).label("total_requests"),
            func.sum(UsageRecord.prompt_tokens).label("total_prompt_tokens"),
            func.sum(UsageRecord.completion_tokens).label("total_completion_tokens"),
            func.count(func.distinct(UsageRecord.endpoint)).label("unique_endpoints"),
        )
        if organization_id is not None:
            query = query.where(UsageRecord.organization_id == organization_id)
        if from_date:
            query = query.where(UsageRecord.date >= from_date)
        if to_date:
            query = query.where(UsageRecord.date <= to_date)
        query = query.group_by(UsageRecord.organization_id, UsageRecord.date).order_by(UsageRecord.date.desc())
        rows = session.exec(query).all()
        records = []
        for row in rows:
            org_id_val, date_val, reqs, pt, ct, eps = row
            records.append(UsageSummary(
                organization_id=org_id_val,
                date=date_val,
                total_requests=reqs or 0,
                total_prompt_tokens=pt or 0,
                total_completion_tokens=ct or 0,
                unique_endpoints=eps or 0,
            ))
        return ListUsageResponse(records=records, total=len(records))
