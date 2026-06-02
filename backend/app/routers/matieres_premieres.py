from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_api_key
from app.models.matiere_premiere import MatierePremiere
from app.schemas.matiere_premiere import MatierePremiere as MatierePremiereOut
from app.schemas.matiere_premiere import MatierePremiereCreate

router = APIRouter(prefix="/matieres-premieres", tags=["matieres-premieres"])


@router.get("", response_model=list[MatierePremiereOut])
async def list_matieres(
    q: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    stmt = select(MatierePremiere).order_by(MatierePremiere.nom, MatierePremiere.format)
    if q:
        stmt = stmt.where(MatierePremiere.nom.ilike(f"%{q}%"))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=MatierePremiereOut, status_code=status.HTTP_201_CREATED)
async def create_matiere(
    data: MatierePremiereCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    item = MatierePremiere(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
