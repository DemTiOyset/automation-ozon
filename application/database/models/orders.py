from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import (
    String, Integer, DateTime, Boolean,
    Index, text, Float, BigInteger, ForeignKey, NUMERIC
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.database.db import Base


class Orders(Base):
    __tablename__ = "orders"

    posting_number: Mapped[str] = mapped_column(
        primary_key=True,
        autoincrement=False,
        unique=True,
    )

    status: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    last_event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    shipment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    is_finished: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    items: Mapped[List["OrderItems"]] = relationship(
        "OrderItems",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="raise",
    )


