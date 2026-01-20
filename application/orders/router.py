from fastapi import APIRouter, Body, status, Depends

from application.dependencies.sheets import get_sheets_repo
from application.orders.integrations.google_sheets.repository import SheetsRepository
from application.orders.services.use_case import handle_order_created

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"]
)

@router.post("/notification")
async def notification(
        notification: dict = Body(...),
        repo: SheetsRepository = Depends(get_sheets_repo)
):
    response = await handle_order_created(notification, repo)
    return response






