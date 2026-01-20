from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class SheetColumns:
    # --- ручные (код НЕ пишет) ---
    supplier: str = "Поставщик"
    purchase_price: str = "Закупочная цена"

    # --- автоматические ---
    name: str = "Наименование товара"
    qty: str = "Количество"
    order_number: str = "Номер заказа"
    commission: str = "Комиссия за товар"
    buyer_price: str = "Цена для покупателя (со скидками)"
    payout: str = "Выплата продавцу"
    ship_date: str = "Дата отгрузки"

    # --- служебные ---
    key: str = "__key"
    row_type: str = "__row_type"
    ship_date_iso: str = "__ship_date"


C = SheetColumns()
