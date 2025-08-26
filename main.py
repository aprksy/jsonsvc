from fastapi import FastAPI
from routers import users, products, orders

app = FastAPI(
    title="Dummy JSON Server",
    description="A simple server that returns random JSON responses from predefined arrays",
    version="1.0.0"
)

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])

@app.get("/")
async def root():
    return {
        "message": "Dummy JSON Server is running!",
        "endpoints": [
            "/users/random",
            "/products/random", 
            "/orders/random"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)