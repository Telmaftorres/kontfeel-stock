from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class GollectCreate(BaseModel):
    ref: str = Field(..., max_length=50)
    nom: str = Field(..., max_length=255)
    description: str | None = None
    etat: str = Field("bon_etat", max_length=30)
    stock_actuel: Decimal = Field(Decimal("0"), ge=0)
    photos: str | None = None


class GollectUpdate(BaseModel):
    nom: str | None = Field(None, max_length=255)
    description: str | None = None
    etat: str | None = Field(None, max_length=30)
    photos: str | None = None


class GollectMovement(BaseModel):
    type: str = Field(..., pattern="^(entree|sortie)$")
    quantite: Decimal = Field(..., gt=0)
    employe: str = Field("Anonyme", max_length=100)


class GollectOut(BaseModel):
    id: int
    ref: str
    nom: str
    description: str | None
    etat: str
    stock_actuel: Decimal
    photos: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
