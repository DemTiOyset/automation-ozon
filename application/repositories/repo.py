from datetime import datetime
from typing import List

from sqlalchemy import select, update

from application.database.db import async_session_maker
from application.database.models.orders import Orders

class OrderRepository:
    @staticmethod
    async def get_order_items_by_posting_number(
            posting_number: str,
    ) -> Orders:
        async with async_session_maker() as session:
            async with session.begin():
                stmt = (select(Orders)
                        .where(Orders.posting_number == posting_number)
                        )

                result = await session.execute(stmt)
                orders = result.scalars().all()

                return orders

    @staticmethod
    async def get_first_order_by_posting_number(
            posting_number: str
    ):
        async with async_session_maker() as session:
            async with session.begin():
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
            orders: List[Orders],
    ) -> List[Orders]:
        async with async_session_maker() as session:
            async with session.begin():
                session.add_all(orders)
                await session.flush()

                return orders

    @staticmethod
    async def cancel_order_items(
            orders: Orders,
    ) -> Orders:
        async with async_session_maker() as session:
            async with session.begin():
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
            posting_number: str,
            shipment_date: datetime,
    ) -> Orders:
        async with async_session_maker() as session:
            async with session.begin():
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
            posting_number: str,
            status: str,
    ) -> Orders:
        async with async_session_maker() as session:
            async with session.begin():
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
    async def update_order_delivery_date_items(
            orders: Orders,
    ) -> Orders:
        async with async_session_maker() as session:
            async with session.begin():
                stmt = (
                    update(Orders)
                    .where(
                        Orders.posting_number == orders.posting_number,
                        Orders.is_returned.is_(False),
                    )
                    .values(
                        delivery_date_begin=orders.delivery_date_begin,
                        delivery_date_end=orders.delivery_date_end,
                    )
                    .returning(Orders)
                )

                result = await session.execute(stmt)
                updated_orders = result.scalars().all()

                return updated_orders


