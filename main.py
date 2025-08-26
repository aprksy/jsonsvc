from fastapi import FastAPI
from routers import users, products, orders, finance, hr

app = FastAPI(
    title="Dummy JSON Server",
    description="A simple server that returns random JSON responses from predefined arrays",
    version="1.0.0"
)

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(finance.router, prefix="/finance", tags=["finance"])
app.include_router(hr.router, prefix="/hr", tags=["hr"])

@app.get("/")
async def root():
    return {
        "message": "Dummy JSON Server is running!",
        "endpoints": [
            "/users/random",
            "/products/random", 
            "/orders/random",
            "/finance/budgets",
            "/finance/expenses",
            "/finance/revenues",
            "/finance/summary",
            "/hr/employees",
            "/hr/policies",
            "/hr/payroll",
            "/hr/summary"
        ],
        "api_keys_note": "Financial and HR endpoints require API key header: X-API-Key"
    }

@app.get("/api-keys")
async def get_api_keys():
    """Endpoint to show available API keys (for testing)"""
    from routers.finance import VALID_API_KEYS
    from routers.hr import VALID_HR_API_KEYS
    
    return {
        "financial_api_keys": VALID_API_KEYS,
        "hr_api_keys": VALID_HR_API_KEYS,
        "usage_note": "Use header: X-API-Key: [key_value]"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)