from fastapi.responses import JSONResponse
from fastapi import status

from application.orders.integrations.google_sheets.repository import SheetsRepository
from application.orders.integrations.market.client import get_order
from application.orders.repo import OrderRepository
from application.orders.services.manage_repo import _create_order_with_items, _dto_to_order
from application.orders.services.manage_sheets import _create_order_items_in_sheets
from application.orders.services.manage_transformation import _transforming_order_creation_data
from application.orders.shemas.notification import OrderCreatedNotificationDTO


async def handle_order_created(
        notification: OrderCreatedNotificationDTO,
        repo: SheetsRepository,
):
    try:
        order_from_market = await get_order(notification.posting_number)
        orders_from_db = \
            await OrderRepository.get_order_items_by_posting_number(notification.posting_number)

        if len(orders_from_db) == 0:
            order_items_dto = await _transforming_order_creation_data(
                order_data=order_from_market
            )

            dto_to_model = [_dto_to_order(dto) for dto in order_items_dto]
            print(order_items_dto, notification, order_from_market)

            orders = await _create_order_with_items(dto_to_model)

            if not orders:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "error": {
                            "code": "ERROR_UNKNOWN",
                            "message": "Failed to write to the database.",
                            "details": None,
                        }
                    },
                )

        order_items_to_sheet = await _create_order_items_in_sheets(repo, order_items_dto)

        if not order_items_to_sheet:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": "ERROR_UNKNOWN",
                        "message": "Failed to write to the sheets.",
                        "details": None,
                    }
                },
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "ERROR_UNKNOWN",
                    "message": "Unknown error.",
                    "details": str(e),
                }
            },
        )

    return JSONResponse(status_code=200, content={"result": True})


