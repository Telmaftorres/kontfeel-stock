from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import generate_key, hash_key, require_api_key
from app.models.api_key import ApiKey
from app.models.webhook import Webhook
from app.schemas.webhook import ApiKeyCreate, ApiKeyOut, WebhookCreate, WebhookOut

router = APIRouter(prefix="/admin", tags=["admin"])


# ── Clés API ─────────────────────────────────────────────

@router.post("/api-keys", response_model=ApiKeyOut, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    raw, hashed = generate_key()
    key = ApiKey(name=data.name, key_hash=hashed, created_at=datetime.now(timezone.utc))
    db.add(key)
    await db.commit()
    await db.refresh(key)
    return ApiKeyOut(id=key.id, name=key.name, key=raw, created_at=key.created_at)


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    result = await db.execute(select(ApiKey).where(ApiKey.id == key_id))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clé introuvable")
    key.is_active = False
    await db.commit()


# ── Webhooks ─────────────────────────────────────────────

@router.get("/webhooks", response_model=list[WebhookOut])
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    result = await db.execute(select(Webhook).order_by(Webhook.created_at.desc()))
    return result.scalars().all()


@router.post("/webhooks", response_model=WebhookOut, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    data: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    wh = Webhook(**data.model_dump(), created_at=datetime.now(timezone.utc))
    db.add(wh)
    await db.commit()
    await db.refresh(wh)
    return wh


@router.delete("/webhooks/{wh_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    wh_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    result = await db.execute(select(Webhook).where(Webhook.id == wh_id))
    wh = result.scalar_one_or_none()
    if not wh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook introuvable")
    await db.delete(wh)
    await db.commit()
