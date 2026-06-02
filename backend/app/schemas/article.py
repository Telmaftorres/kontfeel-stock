from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ArticleCreate(BaseModel):
    ref: str = Field(..., max_length=50)
    nom: str = Field(..., max_length=255)
    zone: str = Field(..., max_length=50)
    unite: str = Field("unité", max_length=50)
    conditionnement: str = Field("aucun", max_length=50)
    format: str | None = Field(None, max_length=50)
    stock_actuel: Decimal = Field(Decimal("0"), ge=0)
    stock_mini: Decimal = Field(Decimal("0"), ge=0)
    prix_unitaire: Decimal | None = Field(None, ge=0)
    photos: str | None = None


class ArticleUpdate(BaseModel):
    nom: str | None = Field(None, max_length=255)
    zone: str | None = Field(None, max_length=50)
    unite: str | None = Field(None, max_length=50)
    format: str | None = Field(None, max_length=50)
    conditionnement: str | None = Field(None, max_length=50)
    stock_mini: Decimal | None = Field(None, ge=0)
    prix_unitaire: Decimal | None = Field(None, ge=0)
    photos: str | None = None


class ArticleOut(BaseModel):
    id: int
    ref: str
    nom: str
    zone: str
    unite: str
    format: str | None
    conditionnement: str
    stock_actuel: Decimal
    stock_mini: Decimal
    prix_unitaire: Decimal | None
    photos: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
