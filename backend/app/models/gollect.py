from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GollectItem(Base):
    __tablename__ = "gollect_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ref: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    etat: Mapped[str] = mapped_column(String(30), nullable=False, default="bon_etat")
    stock_actuel: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=0)
    photos: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
