from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Movement(Base):
    __tablename__ = "movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_ref: Mapped[str] = mapped_column(String(50), ForeignKey("articles.ref"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'entree' | 'sortie'
    quantite: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    stock_avant: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    stock_apres: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    cout: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)  # quantite × prix_unitaire
    employe: Mapped[str] = mapped_column(String(100), nullable=False, default="Anonyme")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="stock-app")  # qui a déclenché
    etude_ref: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
