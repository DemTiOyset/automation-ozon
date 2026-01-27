"""
    Это Use Case слой, который оркестрирует сценарии бизнес-логики проекта:
        1. Создание заказа
        2. Обновление заказа (статус, дата отгрузки, даты начала и конца заказа)
        3. Отмена заказа
    Данный слой независим от контрактов
"""

from application.orders.integrations.google_sheets.repository import SheetsRepository
from application.orders.integrations.market.client import get_order
from application.orders.repo import OrderRepository
from application.orders.responses import Responses
from application.orders.services.manage_repo import _create_order_with_items, _dto_to_order, _update_order_shipment_date
from application.orders.services.manage_sheets import _create_order_items_in_sheets
from application.orders.services.manage_transformation import _transforming_order_data
from application.orders.shemas.notification import OrderCreatedNotificationDTO, OrderUpdatedShipmentDateNotificationDTO


async def handle_order_created(
        notification: OrderCreatedNotificationDTO,
        repo: SheetsRepository,
):
    try:
        order_from_market = await get_order(notification.posting_number)    # Получение заказа с озона по его номеру из вебхука
        orders_from_db = \
            await OrderRepository.get_order_items_by_posting_number(notification.posting_number)    # Получение записи заказа из бд по его номеру из вебхука

        if len(orders_from_db) == 0:    # Проверка на наличие записи о заказе в бд, если записей нет, то программа записывает
            order_items_dto = await _transforming_order_data(
                order_data=order_from_market
            )   # Преобразование данных полученных из get_order в pydantic схему, которую можно преобразовать в ORM модель

            dto_to_model = [_dto_to_order(dto) for dto in order_items_dto]  # Преобразование pydantic схемы в ORM модель

            orders = await _create_order_with_items(dto_to_model)   # Создание записи в бд

            if not orders:  # Проверка того созданы ли записи в бд
                return Responses.responses(
                    {"message": "Order creation in database failed"}
                )

        order_items_to_sheet = await _create_order_items_in_sheets(repo, order_items_dto)   # Создание записи о заказе в таблице

        if not order_items_to_sheet:    # Проверка наличия записи в таблице
            return Responses.responses(
                {"message": "Order creation in sheet failed"}
            )

    except Exception as e:  # Отлов ошибок
        return Responses.responses(
            {"message": "Unknown error", "error": str(e)}
        )

    return Responses.responses(
        {"message": "Ok"}
    )


async def handle_order_updated_shipment_date(
        notification: OrderUpdatedShipmentDateNotificationDTO,
        repo: SheetsRepository,
):
    try:
        order_from_market = await get_order(notification.posting_number)    # Получение заказа с озона по его номеру из вебхука
        orders_from_db = \
            await OrderRepository.get_order_items_by_posting_number(notification.posting_number)    # Получение записи заказа из бд по его номеру из вебхука

        if order_from_market == 0:
            return {"message": "There is no such entry in the database"}

        shipment_date_from_db = await OrderRepository.get_shipment_dates(
            notification.posting_number,
        )

        if shipment_date_from_db == notification.new_cutoff_date:
            return Responses.responses(
                {"message": "New cutoff date equal to the entry in the database"}
            )

        orders = await _update_order_shipment_date(notification.new_cutoff_date)
        
        if not orders:
            return Responses.responses(
                {"message": "Order creation in database failed"}
            )
        
        # Написать обновление в таблицах

    except Exception as e:  # Отлов ошибок
        return Responses.responses(
            {"message": "Unknown error", "error": str(e)}
        )
            
    return Responses.responses(
        {"message": "Ok"}
    )



