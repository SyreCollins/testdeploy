from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.keys.service import store as api_key_store
from app.core.config import get_settings
from app.db.engine import get_engine
from app.db.models.platform import ApiKey as ApiKeyModel
from app.db.models.platform import Organization, Project, User

router = APIRouter(prefix="/v1/organizations", tags=["organizations"])


def _get_session():
    engine = get_engine(get_settings().database_url)
    with Session(engine) as session:
        yield session


def _get_org(request: Request, session: Session) -> Organization:
    org_id = getattr(request.state, "org_id", None) or getattr(request.state, "organization_id", None)
    if org_id is None:
        raise HTTPException(status_code=401, detail="Organization not identified")
    org = session.get(Organization, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


class OrgDetail(BaseModel):
    id: int
    clerk_org_id: str
    name: str
    slug: str
    plan: str
    is_active: bool
    created_at: datetime
    member_count: int = 0
    project_count: int = 0


@router.get("/me")
async def get_org_me(request: Request) -> OrgDetail:
    with Session(get_engine(get_settings().database_url)) as session:
        org = _get_org(request, session)
        from sqlmodel import func

        member_count = session.exec(
            select(func.count()).select_from(User).where(User.organization_id == org.id)
        ).one()
        project_count = session.exec(
            select(func.count()).select_from(Project).where(Project.organization_id == org.id)
        ).one()
        return OrgDetail(
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


class UsageEndpoint(BaseModel):
    endpoint: str
    request_count: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0


class UsageTotals(BaseModel):
    total_requests: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0


class OrgUsageResponse(BaseModel):
    organization_id: int
    from_date: str
    to_date: str
    endpoints: list[UsageEndpoint] = []
    totals: UsageTotals


@router.get("/me/usage")
async def get_org_usage(
    request: Request,
    from_date: str = Query(default=None, alias="from"),
    to_date: str = Query(default=None, alias="to"),
) -> OrgUsageResponse:
    with Session(get_engine(get_settings().database_url)) as session:
        org = _get_org(request, session)
        from app.db.models.usage import UsageRecord

        query = select(UsageRecord).where(UsageRecord.organization_id == org.id)
        if from_date:
            query = query.where(UsageRecord.date >= from_date)
        if to_date:
            query = query.where(UsageRecord.date <= to_date)

        records = session.exec(query).all()

        endpoint_map: dict[str, dict] = {}
        totals = {"total_requests": 0, "total_prompt_tokens": 0, "total_completion_tokens": 0}

        for r in records:
            if r.endpoint not in endpoint_map:
                endpoint_map[r.endpoint] = {
                    "endpoint": r.endpoint, "request_count": 0,
                    "prompt_tokens": 0, "completion_tokens": 0,
                }
            endpoint_map[r.endpoint]["request_count"] += r.request_count or 0
            endpoint_map[r.endpoint]["prompt_tokens"] += r.prompt_tokens or 0
            endpoint_map[r.endpoint]["completion_tokens"] += r.completion_tokens or 0
            totals["total_requests"] += r.request_count or 0
            totals["total_prompt_tokens"] += r.prompt_tokens or 0
            totals["total_completion_tokens"] += r.completion_tokens or 0

        return OrgUsageResponse(
            organization_id=org.id,
            from_date=from_date or "",
            to_date=to_date or "",
            endpoints=[UsageEndpoint(**v) for v in endpoint_map.values()],
            totals=UsageTotals(**totals),
        )


class ApiKeyItem(BaseModel):
    id: str
    label: str
    prefix: str
    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool
    last_used_at: datetime | None = None


class ListApiKeysResponse(BaseModel):
    keys: list[ApiKeyItem]


@router.get("/me/api-keys")
async def list_org_api_keys(request: Request) -> ListApiKeysResponse:
    org_id = getattr(request.state, "org_id", None)
    if org_id is None:
        raise HTTPException(status_code=401, detail="Organization not identified")
    keys = api_key_store.list_keys(organization_id=org_id)
    return ListApiKeysResponse(
        keys=[ApiKeyItem(**{k: v for k, v in key.items() if k in ApiKeyItem.model_fields}) for key in keys]
    )


class CreateApiKeyRequest(BaseModel):
    label: str
    expires_at: datetime | None = None


class CreateApiKeyResponse(BaseModel):
    id: str
    label: str
    key: str
    prefix: str
    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool


@router.post("/me/api-keys", status_code=201)
async def create_org_api_key(request: Request, body: CreateApiKeyRequest) -> CreateApiKeyResponse:
    org_id = getattr(request.state, "org_id", None)
    if org_id is None:
        raise HTTPException(status_code=401, detail="Organization not identified")
    result = api_key_store.create_key(
        label=body.label,
        organization_id=org_id,
        expires_at=body.expires_at,
    )
    return CreateApiKeyResponse(**result)


class RotateApiKeyResponse(BaseModel):
    id: str
    key: str


@router.post("/me/api-keys/{key_id}/rotate")
async def rotate_org_api_key(request: Request, key_id: str) -> RotateApiKeyResponse:
    org_id = getattr(request.state, "org_id", None)
    if org_id is None:
        raise HTTPException(status_code=401, detail="Organization not identified")

    entry = api_key_store.get_key(key_id)
    if entry is None or entry.get("organization_id") != org_id:
        raise HTTPException(status_code=404, detail="API key not found")

    result = api_key_store.rotate_key(key_id)
    if result is None:
        raise HTTPException(status_code=404, detail="API key not found")
    return RotateApiKeyResponse(id=result["id"], key=result["key"])


class RevokeApiKeyResponse(BaseModel):
    id: str
    revoked: bool


@router.post("/me/api-keys/{key_id}/revoke")
async def revoke_org_api_key(request: Request, key_id: str) -> RevokeApiKeyResponse:
    org_id = getattr(request.state, "org_id", None)
    if org_id is None:
        raise HTTPException(status_code=401, detail="Organization not identified")

    entry = api_key_store.get_key(key_id)
    if entry is None or entry.get("organization_id") != org_id:
        raise HTTPException(status_code=404, detail="API key not found")

    result = api_key_store.revoke_key(key_id)
    return RevokeApiKeyResponse(id=key_id, revoked=result)


class ProjectDetail(BaseModel):
    id: int
    name: str
    slug: str
    environment: str
    organization_id: int
    created_at: datetime


class ListProjectsResponse(BaseModel):
    projects: list[ProjectDetail]


class CreateProjectRequest(BaseModel):
    name: str
    slug: str
    environment: str = "production"


class UpdateProjectRequest(BaseModel):
    name: str | None = None
    slug: str | None = None
    environment: str | None = None


@router.get("/me/projects")
async def list_projects(request: Request) -> ListProjectsResponse:
    with Session(get_engine(get_settings().database_url)) as session:
        org = _get_org(request, session)
        projects = session.exec(
            select(Project).where(Project.organization_id == org.id)
        ).all()
        return ListProjectsResponse(
            projects=[ProjectDetail(
                id=p.id, name=p.name, slug=p.slug,
                environment=p.environment, organization_id=p.organization_id,
                created_at=p.created_at,
            ) for p in projects]
        )


@router.post("/me/projects", status_code=201)
async def create_project(request: Request, body: CreateProjectRequest) -> ProjectDetail:
    with Session(get_engine(get_settings().database_url)) as session:
        org = _get_org(request, session)
        existing = session.exec(
            select(Project).where(
                Project.organization_id == org.id,
                Project.slug == body.slug,
            )
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Project slug already exists in this organization")
        project = Project(
            name=body.name,
            slug=body.slug,
            environment=body.environment,
            organization_id=org.id,
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        return ProjectDetail(
            id=project.id, name=project.name, slug=project.slug,
            environment=project.environment, organization_id=project.organization_id,
            created_at=project.created_at,
        )


def _get_project(org: Organization, project_id: int, session: Session) -> Project:
    project = session.get(Project, project_id)
    if project is None or project.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/me/projects/{project_id}")
async def get_project(request: Request, project_id: int) -> ProjectDetail:
    with Session(get_engine(get_settings().database_url)) as session:
        org = _get_org(request, session)
        project = _get_project(org, project_id, session)
        return ProjectDetail(
            id=project.id, name=project.name, slug=project.slug,
            environment=project.environment, organization_id=project.organization_id,
            created_at=project.created_at,
        )


@router.patch("/me/projects/{project_id}")
async def update_project(request: Request, project_id: int, body: UpdateProjectRequest) -> ProjectDetail:
    with Session(get_engine(get_settings().database_url)) as session:
        org = _get_org(request, session)
        project = _get_project(org, project_id, session)
        if body.name is not None:
            project.name = body.name
        if body.slug is not None:
            existing_slug = session.exec(
                select(Project).where(
                    Project.organization_id == org.id,
                    Project.slug == body.slug,
                    Project.id != project_id,
                )
            ).first()
            if existing_slug:
                raise HTTPException(status_code=409, detail="Project slug already exists")
            project.slug = body.slug
        if body.environment is not None:
            project.environment = body.environment
        session.add(project)
        session.commit()
        session.refresh(project)
        return ProjectDetail(
            id=project.id, name=project.name, slug=project.slug,
            environment=project.environment, organization_id=project.organization_id,
            created_at=project.created_at,
        )


@router.delete("/me/projects/{project_id}")
async def delete_project(request: Request, project_id: int) -> dict:
    with Session(get_engine(get_settings().database_url)) as session:
        org = _get_org(request, session)
        project = _get_project(org, project_id, session)
        api_keys = session.exec(
            select(ApiKeyModel).where(ApiKeyModel.project_id == project_id)
        ).all()
        for key in api_keys:
            key.is_active = False
            session.add(key)
        session.delete(project)
        session.commit()
    return {"status": "deleted"}


class ProjectApiKeyListResponse(BaseModel):
    keys: list[ApiKeyItem]


@router.get("/me/projects/{project_id}/api-keys")
async def list_project_api_keys(request: Request, project_id: int) -> ProjectApiKeyListResponse:
    with Session(get_engine(get_settings().database_url)) as session:
        org = _get_org(request, session)
        _get_project(org, project_id, session)
    keys = api_key_store.list_keys(organization_id=org.id)
    project_keys = [k for k in keys if k.get("project_id") == project_id]
    return ProjectApiKeyListResponse(
        keys=[ApiKeyItem(**{k: v for k, v in key.items() if k in ApiKeyItem.model_fields}) for key in project_keys]
    )


@router.post("/me/projects/{project_id}/api-keys", status_code=201)
async def create_project_api_key(request: Request, project_id: int, body: CreateApiKeyRequest) -> CreateApiKeyResponse:
    org_id = getattr(request.state, "org_id", None)
    if org_id is None:
        raise HTTPException(status_code=401, detail="Organization not identified")
    result = api_key_store.create_key(
        label=body.label,
        organization_id=org_id,
        project_id=project_id,
        expires_at=body.expires_at,
    )
    return CreateApiKeyResponse(**result)


@router.post("/me/projects/{project_id}/api-keys/{key_id}/rotate")
async def rotate_project_api_key(request: Request, project_id: int, key_id: str) -> RotateApiKeyResponse:
    org_id = getattr(request.state, "org_id", None)
    if org_id is None:
        raise HTTPException(status_code=401, detail="Organization not identified")
    entry = api_key_store.get_key(key_id)
    if entry is None or entry.get("organization_id") != org_id or entry.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail="API key not found")
    result = api_key_store.rotate_key(key_id)
    if result is None:
        raise HTTPException(status_code=404, detail="API key not found")
    return RotateApiKeyResponse(id=result["id"], key=result["key"])


@router.post("/me/projects/{project_id}/api-keys/{key_id}/revoke")
async def revoke_project_api_key(request: Request, project_id: int, key_id: str) -> RevokeApiKeyResponse:
    org_id = getattr(request.state, "org_id", None)
    if org_id is None:
        raise HTTPException(status_code=401, detail="Organization not identified")
    entry = api_key_store.get_key(key_id)
    if entry is None or entry.get("organization_id") != org_id or entry.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail="API key not found")
    result = api_key_store.revoke_key(key_id)
    return RevokeApiKeyResponse(id=key_id, revoked=result)
