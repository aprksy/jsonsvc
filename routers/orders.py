from fastapi import APIRouter, HTTPException
import json
import random
from pathlib import Path

router = APIRouter()

def load_order_data():
    data_file = Path("data/orders.json")
    if not data_file.exists():
        default_data = [
            {"id": 1, "user_id": 1, "total": 150.99, "status": "completed"},
            {"id": 2, "user_id": 2, "total": 299.99, "status": "processing"},
            {"id": 3, "user_id": 1, "total": 45.50, "status": "shipped"},
            {"id": 4, "user_id": 3, "total": 89.99, "status": "completed"},
            {"id": 5, "user_id": 4, "total": 1200.00, "status": "pending"}
        ]
        data_file.parent.mkdir(exist_ok=True)
        data_file.write_text(json.dumps(default_data, indent=2))
        return default_data
    
    return json.loads(data_file.read_text())

@router.get("/random")
async def get_random_order():
    orders = load_order_data()
    if not orders:
        raise HTTPException(status_code=404, detail="No order data available")
    return random.choice(orders)

@router.get("/all")
async def get_all_orders():
    return load_order_data()

@router.get("/user/{user_id}")
async def get_orders_by_user(user_id: int):
    orders = load_order_data()
    filtered = [o for o in orders if o.get("user_id") == user_id]
    if not filtered:
        raise HTTPException(status_code=404, detail=f"No orders found for user {user_id}")
    return filtered