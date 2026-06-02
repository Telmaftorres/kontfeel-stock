from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_api_key
from app.models.gollect import GollectItem
from app.schemas.gollect import GollectCreate, GollectMovement, GollectOut, GollectUpdate

router = APIRouter(prefix="/gollect", tags=["gollect"])


@router.get("", response_model=list[GollectOut])
async def list_gollect(
    q: str | None = Query(None),
    etat: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    stmt = select(GollectItem).order_by(GollectItem.nom)
    if q:
        stmt = stmt.where(GollectItem.nom.ilike(f"%{q}%") | GollectItem.ref.ilike(f"%{q}%"))
    if etat:
        stmt = stmt.where(GollectItem.etat == etat)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=GollectOut, status_code=status.HTTP_201_CREATED)
async def create_gollect(
    data: GollectCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    existing = await db.execute(select(GollectItem).where(GollectItem.ref == data.ref))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Référence déjà utilisée")

    item = GollectItem(**data.model_dump(), created_at=datetime.now(timezone.utc))
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/{ref}", response_model=GollectOut)
async def get_gollect(
    ref: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    result = await db.execute(select(GollectItem).where(GollectItem.ref == ref))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article introuvable")
    return item


@router.patch("/{ref}", response_model=GollectOut)
async def update_gollect(
    ref: str,
    data: GollectUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    result = await db.execute(select(GollectItem).where(GollectItem.ref == ref))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article introuvable")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    item.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(item)
    return item


@router.post("/{ref}/movement", response_model=GollectOut)
async def gollect_movement(
    ref: str,
    data: GollectMovement,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    result = await db.execute(select(GollectItem).where(GollectItem.ref == ref))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article introuvable")

    if data.type == "entree":
        item.stock_actuel += data.quantite
    else:
        item.stock_actuel = max(Decimal("0"), item.stock_actuel - data.quantite)
    item.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(item)
    return item


@router.post("/{ref}/photo", response_model=GollectOut)
async def add_gollect_photo(
    ref: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    result = await db.execute(select(GollectItem).where(GollectItem.ref == ref))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article introuvable")

    url = body.get("url")
    if not url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="url manquante")

    existing = item.photos + "," if item.photos else ""
    item.photos = existing + url
    item.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(item)
    return item
