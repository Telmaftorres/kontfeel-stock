from datetime import datetime

from pydantic import BaseModel, HttpUrl


class WebhookCreate(BaseModel):
    name: str
    url: str
    secret: str | None = None
    events: str = "movement"    # "movement" | "movement.sortie" | "movement.entree"


class WebhookOut(BaseModel):
    id: int
    name: str
    url: str
    events: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreate(BaseModel):
    name: str


class ApiKeyOut(BaseModel):
    id: int
    name: str
    key: str        # seulement à la création, jamais après
    created_at: datetime
