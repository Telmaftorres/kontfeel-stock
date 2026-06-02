from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_api_key
from app.models.article import Article
from app.models.movement import Movement
from app.schemas.movement import MovementCreate, MovementOut
from app.services.webhook_service import dispatch

router = APIRouter(prefix="/movements", tags=["movements"])


@router.post("", response_model=MovementOut, status_code=status.HTTP_201_CREATED)
async def record_movement(
    data: MovementCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    result = await db.execute(select(Article).where(Article.ref == data.article_ref))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article introuvable")

    stock_avant = article.stock_actuel
    if data.type == "entree":
        stock_apres = stock_avant + data.quantite
    else:
        stock_apres = max(Decimal("0"), stock_avant - data.quantite)

    cout = None
    if article.prix_unitaire and data.type == "sortie":
        cout = data.quantite * article.prix_unitaire

    article.stock_actuel = stock_apres
    article.updated_at = datetime.now(timezone.utc)

    movement = Movement(
        article_ref=data.article_ref,
        type=data.type,
        quantite=data.quantite,
        stock_avant=stock_avant,
        stock_apres=stock_apres,
        cout=cout,
        employe=data.employe,
        notes=data.notes,
        source=data.source,
        created_at=datetime.now(timezone.utc),
    )
    db.add(movement)
    await db.commit()
    await db.refresh(movement)

    # Dispatch webhook en arrière-plan (non bloquant)
    payload = {
        "event": f"movement.{data.type}",
        "movement": {
            "id": movement.id,
            "article_ref": movement.article_ref,
            "article_nom": article.nom,
            "type": movement.type,
            "quantite": float(movement.quantite),
            "stock_avant": float(movement.stock_avant),
            "stock_apres": float(movement.stock_apres),
            "cout": float(movement.cout) if movement.cout else None,
            "employe": movement.employe,
            "source": movement.source,
            "created_at": movement.created_at.isoformat(),
        },
    }
    await dispatch(db, f"movement.{data.type}", payload)

    return movement


@router.get("", response_model=list[MovementOut])
async def list_movements(
    article_ref: str | None = Query(None),
    type: str | None = Query(None),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    stmt = select(Movement).order_by(Movement.created_at.desc()).limit(limit)
    if article_ref:
        stmt = stmt.where(Movement.article_ref == article_ref)
    if type:
        stmt = stmt.where(Movement.type == type)
    result = await db.execute(stmt)
    return result.scalars().all()
