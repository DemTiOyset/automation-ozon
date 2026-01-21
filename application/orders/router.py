from fastapi import APIRouter, Body, status, Depends
from pydantic import ValidationError
from fastapi.responses import JSONResponse

from application.dependencies.sheets import get_sheets_repo
from application.orders.integrations.google_sheets.repository import SheetsRepository
from application.orders.services.use_case import handle_order_created
from application.orders.shemas.notification import OrderCreatedNotificationDTO, NotificationTypeEnum

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"]
)

@router.post("/notification")
async def notification(
        unprocessed_notification: dict = Body(...),
        repo: SheetsRepository = Depends(get_sheets_repo)
):
    if unprocessed_notification.get("message_type") == NotificationTypeEnum.TYPE_PING:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
               "version": "1.0.0",
               "name": "Gorbushka Keepers Ozon",
               "time": unprocessed_notification.get("time")
            }
        )

    try:
        notification = OrderCreatedNotificationDTO.model_validate(unprocessed_notification)
    except ValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "ERROR_UNKNOWN",
                    "message": "Failed to write to the database.",
                    "details": None,
                }
            },
        )

    response = await handle_order_created(notification, repo)
    return response






