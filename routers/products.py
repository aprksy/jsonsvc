from fastapi import APIRouter, HTTPException
import json
import random
from pathlib import Path

router = APIRouter()

def load_product_data():
    data_file = Path("data/products.json")
    if not data_file.exists():
        default_data = [
            {"id": 1, "name": "Laptop", "price": 999.99, "category": "electronics"},
            {"id": 2, "name": "Smartphone", "price": 699.99, "category": "electronics"},
            {"id": 3, "name": "Headphones", "price": 149.99, "category": "electronics"},
            {"id": 4, "name": "Book", "price": 19.99, "category": "education"},
            {"id": 5, "name": "Coffee Mug", "price": 12.99, "category": "home"}
        ]
        data_file.parent.mkdir(exist_ok=True)
        data_file.write_text(json.dumps(default_data, indent=2))
        return default_data
    
    return json.loads(data_file.read_text())

@router.get("/random")
async def get_random_product():
    products = load_product_data()
    if not products:
        raise HTTPException(status_code=404, detail="No product data available")
    return random.choice(products)

@router.get("/all")
async def get_all_products():
    return load_product_data()

@router.get("/category/{category}")
async def get_products_by_category(category: str):
    products = load_product_data()
    filtered = [p for p in products if p.get("category", "").lower() == category.lower()]
    if not filtered:
        raise HTTPException(status_code=404, detail=f"No products found in category '{category}'")
    return filtered