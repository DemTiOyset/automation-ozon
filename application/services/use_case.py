"""
    Это Use Case слой, который оркестрирует сценарии бизнес-логики проекта:
        1. Создание заказа
        2. Обновление заказа (статус, дата отгрузки, даты начала и конца заказа)
        3. Отмена заказа
    Данный слой независим от контрактов
"""
from sqlalchemy.ext.asyncio import AsyncSession

from application.clients.market.client import get_order
from application.repositories.google_sheets.repository import SheetsRepository
from application.repositories.repo import OrderRepository
from application.services.sheets import _create_order_items_in_sheets
from application.sсhemas.transformation import transforming_order_data_creation, dto_to_order, \
    transforming_order_items_creation, dto_to_order_items
from application.sсhemas.notification import OrderCreatedNotificationDTO, OrderUpdatedShipmentDateNotificationDTO, \
    OrderUpdatedStatusNotificationDTO, OrderCancelledNotificationDTO


async def handle_order_created(
        notification: OrderCreatedNotificationDTO,
        sheet_repo: SheetsRepository,
        session: AsyncSession
):
    try:
        order_from_market = await get_order(notification.posting_number)
        order_from_db = \
            await OrderRepository.get_first_order_by_posting_number(session, notification.posting_number)    # Получение записи заказа из бд по его номеру из вебхука

        order_dto = await transforming_order_data_creation(
            order_data=order_from_market
        )  # Преобразование данных полученных из get_order в pydantic схему, которую можно преобразовать в ORM модель

        order_items_dto = await transforming_order_items_creation(
            order_data=order_from_market
        )

        if not order_from_db:    # Проверка на наличие записи о заказе в бд, если записей нет, то программа записывает
            dto_items_to_model = [dto_to_order_items(dto) for dto in order_items_dto]  # Преобразование pydantic схемы в ORM модель
            dto_order_to_model = dto_to_order(order_dto)


            orders = await OrderRepository.create_order_with_items(session, dto_order_to_model, dto_items_to_model)   # Создание записи в бд

            if not orders:  # Проверка того созданы ли записи в бд
                return {"message": "Order creation in database failed"}
                

        order_items_to_sheet = await _create_order_items_in_sheets(sheet_repo, order_items_dto)   # Создание записи о заказе в таблице

        if not order_items_to_sheet:    # Проверка наличия записи в таблице
            return {"message": "Order creation in sheet failed"}
            

    except Exception as e:  # Отлов ошибок
        return  {"message": "Unknown error", "error": str(e)}
        

    return {"message": "Ok"}
    


async def handle_order_updated_shipment_date(
        notification: OrderUpdatedShipmentDateNotificationDTO,
        sheet_repo: SheetsRepository,
        session: AsyncSession
):
    try:
        orders_from_db = \
            await OrderRepository.get_order_items_by_posting_number(session, notification.posting_number)    # Получение записи заказа из бд по его номеру из вебхука

        if orders_from_db == 0:
            return {"message": "There is no such entry in the database"}

        order = await OrderRepository.get_first_order_by_posting_number(session, notification.posting_number)

        shipment_date_from_db = order.shipment_date

        if shipment_date_from_db == notification.new_cutoff_date:
            return {"message": "New cutoff date equal to the entry in the database"}


        orders = await OrderRepository.update_order_shipment_date(session, notification.posting_number, notification.new_cutoff_date)
        
        if not orders:
            return  {"message": "Order creation in database failed"}
            
        
        # Написать обновление в таблицах

    except Exception as e:  # Отлов ошибок
        return {"message": "Unknown error", "error": str(e)}
        
            
    return {"message": "Ok"}
    

async def handle_order_updated_status(
        notification: OrderUpdatedStatusNotificationDTO,
        sheet_repo: SheetsRepository,
        session: AsyncSession
):
    try:
        orders_from_db = \
            await OrderRepository.get_order_items_by_posting_number(session, notification.posting_number)    # Получение записи заказа из бд по его номеру из вебхука

        if orders_from_db == 0:
            return {"message": "There is no such entry in the database"}

        order = await OrderRepository.get_first_order_by_posting_number(session, notification.posting_number)

        last_event_time_from_db = order.last_event_time

        if last_event_time_from_db >= notification.changed_state_date:
            return {"message": "The changed state date is less than the last change date in the database"}


        orders = await OrderRepository.update_order_status(session, notification.posting_number, notification.new_state)

        if not orders:
            return {"message": "Order creation in database failed"}
            

        # Написать обновление в таблицах

    except Exception as e:  # Отлов ошибок
        return {"message": "Unknown error", "error": str(e)}
        

    return {"message": "Ok"}
    


async def handle_order_items_returned(
        notification: OrderCancelledNotificationDTO,
        sheet_repo: SheetsRepository,
        session: AsyncSession
):
    try:
        orders_from_db = \
            await OrderRepository.get_order_items_by_posting_number(session, notification.posting_number)    # Получение записи заказа из бд по его номеру из вебхука

        if orders_from_db == 0:
            return {"message": "There is no such entry in the database"}

    except Exception as e:  # Отлов ошибок
        return {"message": "Unknown error", "error": str(e)}





