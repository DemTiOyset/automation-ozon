from datetime import datetime
from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.database.models.order_items import OrderItems
from application.database.models.orders import Orders


class OrderRepository:
    @staticmethod
    async def get_order_items_by_posting_number(
            session: AsyncSession,
            posting_number: str,
    ) -> Orders:
        stmt = (select(Orders)
                .where(Orders.posting_number == posting_number)
                )

        result = await session.execute(stmt)
        orders = result.scalars().all()

        return orders

    @staticmethod
    async def get_first_order_by_posting_number(
            session: AsyncSession,
            posting_number: str
    ):
        stmt = (select(Orders)
        .where(
            Orders.posting_number == posting_number
            )
        )

        result = await session.execute(stmt)
        orders_shipment_date = result.scalars().first()

        return orders_shipment_date

    @staticmethod
    async def create_order_with_items(
            session: AsyncSession,
            order: Orders,
            order_items: List[OrderItems],
    ) -> Orders:
        order.items = order_items

        session.add(order)
        await session.flush()

        return order

    @staticmethod
    async def cancel_order_items(
            session: AsyncSession,
            orders: Orders,
    ) -> Orders:
        
        stmt = (
            update(Orders)
            .where(
                Orders.posting_number == orders.posting_number,
                Orders.sku == orders.sku,
                Orders.is_returned.is_(False),
            )
            .values(is_returned=True)
            .returning(Orders)
        )

        result = await session.execute(stmt)
        updated_orders = result.scalars().all()

        return updated_orders

    @staticmethod
    async def update_order_shipment_date(
            session: AsyncSession,
            posting_number: str,
            shipment_date: datetime,
    ) -> Orders:
        stmt = (
            update(Orders)
            .where(
                Orders.posting_number == posting_number,
                Orders.is_returned.is_(False),
            )
            .values(shipment_date=shipment_date)
            .returning(Orders)
        )

        result = await session.execute(stmt)
        updated_orders = result.scalars().all()

        return updated_orders

    @staticmethod
    async def update_order_status(
            session: AsyncSession,
            posting_number: str,
            status: str,
    ) -> Orders:
        
        stmt = (
            update(Orders)
            .where(
                Orders.posting_number == posting_number,
                Orders.is_returned.is_(False),
            )
            .values(status=status)
            .returning(Orders)
        )

        result = await session.execute(stmt)
        orders = result.scalars().all()

        return orders



    @staticmethod
    async def mark_cancelled_items_in_order(
            session: AsyncSession,
            posting_number: str,
            sku: int
    ):
        ...




