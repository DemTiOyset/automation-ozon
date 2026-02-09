from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import (
    String, Integer, DateTime, Boolean,
    Index, text, Float, BigInteger, ForeignKey, NUMERIC
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.database.db import Base


class OrderItems(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_posting_number: Mapped[str] = mapped_column(
        ForeignKey("orders.posting_number", ondelete="CASCADE"),
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    quantity_cancelled: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    commission_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    commission_percent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    payout: Mapped[Decimal] = mapped_column(
        NUMERIC,
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        NUMERIC,
        nullable=False,
    )

    customer_price: Mapped[Decimal] = mapped_column(
        NUMERIC,
        nullable=False,
    )

    total_discount_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    total_discount_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    offer_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    sku: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        unique=True
    )

    is_returned: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    is_returned_finished: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    order: Mapped["Orders"] = relationship(
        "Orders",
        back_populates="items",
    )