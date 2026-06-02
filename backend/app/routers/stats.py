from datetime import datetime, timezone, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_api_key
from app.models.article import Article
from app.models.movement import Movement
from app.schemas.movement import StatsMonth, StatsOut

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsOut)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_api_key),
):
    # Total articles + valeur stock
    art_result = await db.execute(select(Article))
    articles = art_result.scalars().all()
    total_articles = len(articles)
    valeur_stock = sum(
        (a.stock_actuel * a.prix_unitaire for a in articles if a.prix_unitaire),
        Decimal("0"),
    )

    # Mouvements des 12 derniers mois
    since = datetime.now(timezone.utc) - timedelta(days=365)
    mov_result = await db.execute(
        select(Movement).where(Movement.created_at >= since).order_by(Movement.created_at)
    )
    movements = mov_result.scalars().all()

    # Agréger par mois
    by_month: dict[str, dict] = {}
    cout_12_mois = Decimal("0")

    for m in movements:
        key = m.created_at.strftime("%Y-%m")
        if key not in by_month:
            by_month[key] = {"nb_sorties": 0, "nb_entrees": 0, "cout_sorties": Decimal("0"), "quantite_sortie": Decimal("0")}
        if m.type == "sortie":
            by_month[key]["nb_sorties"] += 1
            by_month[key]["quantite_sortie"] += m.quantite
            if m.cout:
                by_month[key]["cout_sorties"] += m.cout
                cout_12_mois += m.cout
        else:
            by_month[key]["nb_entrees"] += 1

    par_mois = [
        StatsMonth(mois=k, **v)
        for k, v in sorted(by_month.items())
    ]

    return StatsOut(
        total_articles=total_articles,
        valeur_stock=valeur_stock,
        cout_12_mois=cout_12_mois,
        par_mois=par_mois,
    )
