from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_api_key
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleOut, ArticleUpdate

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[ArticleOut])
async def list_articles(
    zone: str | None = Query(None),
    q: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    stmt = select(Article)
    if zone:
        stmt = stmt.where(Article.zone == zone)
    if q:
        stmt = stmt.where(Article.nom.ilike(f"%{q}%") | Article.ref.ilike(f"%{q}%"))
    result = await db.execute(stmt.order_by(Article.zone, Article.nom))
    return result.scalars().all()


@router.post("", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
async def create_article(
    data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    existing = await db.execute(select(Article).where(Article.ref == data.ref))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Référence déjà utilisée")

    article = Article(**data.model_dump(), created_at=datetime.now(timezone.utc))
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article


@router.get("/{ref}", response_model=ArticleOut)
async def get_article(
    ref: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    result = await db.execute(select(Article).where(Article.ref == ref))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article introuvable")
    return article


@router.patch("/{ref}", response_model=ArticleOut)
async def update_article(
    ref: str,
    data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    result = await db.execute(select(Article).where(Article.ref == ref))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article introuvable")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(article, field, value)
    article.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(article)
    return article


@router.delete("/{ref}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    ref: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    result = await db.execute(select(Article).where(Article.ref == ref))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article introuvable")
    await db.delete(article)
    await db.commit()
