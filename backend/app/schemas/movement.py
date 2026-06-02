from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class MovementCreate(BaseModel):
    article_ref: str
    type: str = Field(..., pattern="^(entree|sortie)$")
    quantite: Decimal = Field(..., gt=0)
    employe: str = Field("Anonyme", max_length=100)
    notes: str | None = None
    source: str = Field("stock-app", max_length=50)
    etude_ref: str | None = Field(None, max_length=50)


class MovementOut(BaseModel):
    id: int
    article_ref: str
    type: str
    quantite: Decimal
    stock_avant: Decimal
    stock_apres: Decimal
    cout: Decimal | None
    employe: str
    notes: str | None
    source: str
    etude_ref: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StatsMonth(BaseModel):
    mois: str           # "2026-05"
    nb_sorties: int
    nb_entrees: int
    cout_sorties: Decimal
    quantite_sortie: Decimal


class StatsOut(BaseModel):
    total_articles: int
    valeur_stock: Decimal       # somme stock_actuel × prix_unitaire
    cout_12_mois: Decimal       # total sorties sur 12 mois
    par_mois: list[StatsMonth]
