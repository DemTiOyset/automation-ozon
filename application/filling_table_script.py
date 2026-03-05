import httpx
from application.data import data


def filling_table(order_numbers: tuple) -> bool:
    for order_number in order_numbers:
        payload = {
                "message_type": "TYPE_NEW_POSTING",
                "posting_number": order_number,
                "products": [
                    {
                        "sku": 147451939,
                        "offer_id": "Товар2",
                        "quantity": 1
                    }
                ],
                "in_process_at": "2021-01-26T06:56:36.294Z",
                "warehouse_id": 12850503335000,
                "shipment_date": "2021-01-26T06:56:36.294Z",
                "delivery_date_begin": "2025-01-26T06:56:36.294Z",
                "delivery_date_end": "2025-01-26T06:56:36.294Z",
                "seller_id": 1
            }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                url="http://localhost:8000/webhook/notification",
                json=payload
            )
            response.raise_for_status()
            print(f"OK: {response.status_code} — {response.json()}")


if __name__ == "__main__":
    filling_table(data)