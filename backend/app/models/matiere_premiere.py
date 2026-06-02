from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MatierePremiere(Base):
    __tablename__ = "matieres_premieres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    format: Mapped[str] = mapped_column(String(50), nullable=False)
    unite: Mapped[str] = mapped_column(String(50), nullable=False, default="feuille")
