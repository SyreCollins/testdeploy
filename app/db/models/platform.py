from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"

    id: int | None = Field(default=None, primary_key=True)
    clerk_org_id: str = Field(unique=True, index=True)
    name: str
    slug: str = Field(unique=True, index=True)
    plan: str = "free"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    members: list["User"] = Relationship(back_populates="organization")
    projects: list["Project"] = Relationship(back_populates="organization")
    api_keys: list["ApiKey"] = Relationship(back_populates="organization")


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    clerk_user_id: str = Field(unique=True, index=True)
    email: str
    name: str | None = None
    role: str = "member"
    organization_id: int = Field(foreign_key="organizations.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    organization: Organization = Relationship(back_populates="members")


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    slug: str = Field(index=True)
    environment: str = "production"
    organization_id: int = Field(foreign_key="organizations.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    organization: Organization = Relationship(back_populates="projects")
    api_keys: list["ApiKey"] = Relationship(back_populates="project")


class ApiKey(SQLModel, table=True):
    __tablename__ = "api_keys"

    id: str = Field(primary_key=True)
    label: str
    key_hash: str = Field(index=True)
    prefix: str
    is_active: bool = True
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    organization_id: int | None = Field(default=None, foreign_key="organizations.id", index=True)
    project_id: int | None = Field(default=None, foreign_key="projects.id")
    created_by: int | None = None

    organization: Organization | None = Relationship(back_populates="api_keys")
    project: Project | None = Relationship(back_populates="api_keys")
