from pydantic import BaseModel, Field


class MatierePremiere(BaseModel):
    id: int
    nom: str
    format: str
    unite: str

    model_config = {"from_attributes": True}


class MatierePremiereCreate(BaseModel):
    nom: str = Field(..., max_length=255)
    format: str = Field(..., max_length=50)
    unite: str = Field("feuille", max_length=50)
