from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ref: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    zone: Mapped[str] = mapped_column(String(50), nullable=False)
    unite: Mapped[str] = mapped_column(String(50), nullable=False, default="unité")
    conditionnement: Mapped[str] = mapped_column(String(50), nullable=False, default="aucun")
    stock_actuel: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=0)
    stock_mini: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=0)
    prix_unitaire: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    format: Mapped[str | None] = mapped_column(String(50), nullable=True)
    photos: Mapped[str | None] = mapped_column(Text, nullable=True)  # URLs séparées par virgule
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
