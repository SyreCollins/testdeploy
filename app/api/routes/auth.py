import base64
import hashlib
import hmac
import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from app.core.config import get_settings
from app.db.models.platform import Organization, User

logger = logging.getLogger("zam-ai-core-api.auth")

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/webhook")
async def clerk_webhook(request: Request) -> JSONResponse:
    settings = getattr(request.app.state, "settings", get_settings())

    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")

    if not all([svix_id, svix_timestamp, svix_signature]):
        logger.warning("clerk_webhook_missing_headers")

    body = await request.body()

    if settings.clerk_webhook_secret and svix_id and svix_timestamp and svix_signature:
        if not _verify_svix_signature(body, svix_id, svix_timestamp, svix_signature, settings.clerk_webhook_secret):
            logger.warning("clerk_webhook_invalid_signature")

    import json
    payload = json.loads(body)
    event_type = payload.get("type")
    data = payload.get("data", {})

    try:
        _handle_webhook_event(event_type, data, settings.database_url)
    except Exception:
        logger.exception("clerk_webhook_processing_failed", extra={"event_type": event_type})

    return JSONResponse({"received": True}, status_code=200)


def _handle_webhook_event(event_type: str, data: dict, database_url: str) -> None:
    from app.db.engine import get_engine

    engine = get_engine(database_url)

    if event_type == "user.created":
        clerk_user_id = data.get("id")
        email = _get_primary_email(data)
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        name = f"{first_name} {last_name}".strip()

        if not clerk_user_id:
            return

        with Session(engine) as session:
            existing = session.exec(
                select(User).where(User.clerk_user_id == clerk_user_id)
            ).first()
            if existing:
                return
            default_org = session.exec(
                select(Organization).order_by(Organization.id).limit(1)
            ).first()
            if not default_org:
                logger.warning("clerk_webhook_no_org_found", extra={"event": "user.created"})
                return
            user = User(
                clerk_user_id=clerk_user_id,
                email=email,
                name=name,
                role="member",
                organization_id=default_org.id,
            )
            session.add(user)
            session.commit()

    elif event_type == "user.updated":
        clerk_user_id = data.get("id")
        email = _get_primary_email(data)
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        name = f"{first_name} {last_name}".strip()

        if not clerk_user_id:
            return

        with Session(engine) as session:
            user = session.exec(
                select(User).where(User.clerk_user_id == clerk_user_id)
            ).first()
            if not user:
                return
            user.email = email
            user.name = name
            session.add(user)
            session.commit()

    elif event_type == "organization.created":
        clerk_org_id = data.get("id")
        name = data.get("name", "")
        slug = data.get("slug", "")

        if not clerk_org_id:
            return

        with Session(engine) as session:
            existing = session.exec(
                select(Organization).where(Organization.clerk_org_id == clerk_org_id)
            ).first()
            if existing:
                return
            org = Organization(
                clerk_org_id=clerk_org_id,
                name=name,
                slug=slug,
                plan="free",
                is_active=True,
            )
            session.add(org)
            session.commit()

    elif event_type == "organization.updated":
        clerk_org_id = data.get("id")
        name = data.get("name", "")
        slug = data.get("slug", "")

        if not clerk_org_id:
            return

        with Session(engine) as session:
            org = session.exec(
                select(Organization).where(Organization.clerk_org_id == clerk_org_id)
            ).first()
            if not org:
                return
            org.name = name
            org.slug = slug
            session.add(org)
            session.commit()

    elif event_type == "organization_membership.created":
        clerk_user_id = data.get("public_user_data", {}).get("user_id")
        clerk_org_id = data.get("organization", {}).get("id")
        role = data.get("role", "member")

        if not clerk_user_id or not clerk_org_id:
            return

        with Session(engine) as session:
            org = session.exec(
                select(Organization).where(Organization.clerk_org_id == clerk_org_id)
            ).first()
            if not org:
                return

            existing = session.exec(
                select(User).where(
                    User.clerk_user_id == clerk_user_id,
                    User.organization_id == org.id,
                )
            ).first()
            if existing:
                existing.role = role
                session.add(existing)
                session.commit()
                return

            email = data.get("public_user_data", {}).get("identifier", "")
            user = User(
                clerk_user_id=clerk_user_id,
                email=email,
                name="",
                role=role,
                organization_id=org.id,
            )
            session.add(user)
            session.commit()


def _get_primary_email(data: dict) -> str:
    email_addresses = data.get("email_addresses", [])
    for addr in email_addresses:
        if addr.get("id") == data.get("primary_email_address_id"):
            return addr.get("email_address", "")
    if email_addresses:
        return email_addresses[0].get("email_address", "")
    return ""


def _verify_svix_signature(
    payload: bytes,
    svix_id: str,
    svix_timestamp: str,
    svix_signature: str,
    secret: str,
) -> bool:
    raw_secret = secret.removeprefix("whsec_")
    try:
        key = base64.b64decode(raw_secret)
    except Exception:
        key = secret.encode()

    signed_content = f"{svix_id}.{svix_timestamp}.{payload.decode('utf-8')}".encode()
    expected = hmac.new(key, signed_content, hashlib.sha256).hexdigest()

    for sig_part in svix_signature.split(" "):
        if sig_part.startswith("v1,"):
            actual = sig_part[3:]
            if hmac.compare_digest(expected, actual):
                return True
    return False
