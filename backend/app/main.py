from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import require_api_key
from app.models.article import Article
from app.models.gollect import GollectItem
from app.routers import admin, articles, gollect, matieres_premieres, movements, stats
from app.services.export_service import export_all_xlsx

settings = get_settings()

app = FastAPI(
    title="Kontfeel Stock API",
    version="1.0.0",
    description="API de gestion de stock — compatible avec tout logiciel via clé API et webhooks.",
    docs_url="/docs" if settings.is_dev else None,
    redoc_url="/redoc" if settings.is_dev else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router, prefix="/api/v1")
app.include_router(matieres_premieres.router, prefix="/api/v1")
app.include_router(movements.router, prefix="/api/v1")
app.include_router(gollect.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/api/v1/export/xlsx")
async def export_all(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    articles_result  = await db.execute(select(Article).order_by(Article.zone, Article.nom))
    gollect_result   = await db.execute(select(GollectItem).order_by(GollectItem.nom))
    from app.models.movement import Movement
    mvt_result = await db.execute(select(Movement).order_by(Movement.created_at.desc()).limit(500))
    data = export_all_xlsx(articles_result.scalars().all(), gollect_result.scalars().all(), mvt_result.scalars().all())
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=kontfeel-stock.xlsx"},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
