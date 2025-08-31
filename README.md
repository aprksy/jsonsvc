# Dummy JSON Server

A simple FastAPI-based JSON server that returns random JSON responses from predefined arrays. Perfect for testing, development, and prototyping.

## Features

- **Multiple API Categories**: Users, Products, Orders, Financial, HR, and IT endpoints
- **API Key Authentication**: Secure endpoints with role-based API keys
- **Random Data Generation**: Returns random JSON responses from predefined arrays
- **Flexible Filtering**: Query parameters for filtering results
- **Data Persistence**: Automatically generates and saves sample data
- **RESTful Design**: Clean, consistent API structure

## API Categories

### 1. Core Endpoints
- **Users**: Random user data, employee information
- **Products**: Product catalog with categories and pricing
- **Orders**: Order management and tracking

### 2. Business Endpoints
- **Financial**: Budgets, expenses, revenue data with financial reporting
- **HR**: Employee management, policies, payroll information
- **IT**: System status, support tickets, password management

## Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd dummy-json-server
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the server**
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Keys

The server uses API key authentication for sensitive endpoints. Available keys:

| Service | Key Type | Key Value |
|---------|----------|-----------|
| Financial | Read-only | `fin_12345abcde` |
| Financial | Admin | `fin_admin_67890xyz` |
| HR | Read-only | `hr_12345abcde` |
| HR | Admin | `hr_admin_67890xyz` |
| HR | Payroll | `payroll_24680mnop` |
| IT | Read-only | `it_12345abcde` |
| IT | Admin | `it_admin_67890xyz` |
| IT | Support | `it_support_24680mnop` |

View all keys: `GET /api-keys`

## Usage Examples

### Public Endpoints (No API Key Required)
```bash
# Get all available endpoints
curl http://localhost:8000/

# Get random user
curl http://localhost:8000/users/random

# Get random product
curl http://localhost:8000/products/random

# Get random order
curl http://localhost:8000/orders/random
```

### Financial Endpoints (API Key Required)
```bash
# Get budget information
curl -H "X-API-Key: fin_12345abcde" "http://localhost:8000/financial/budgets?department=Engineering"

# Get expense reports
curl -H "X-API-Key: fin_12345abcde" "http://localhost:8000/financial/expenses?date_from=2024-01-01&date_to=2024-03-31"

# Get revenue data
curl -H "X-API-Key: fin_12345abcde" "http://localhost:8000/financial/revenues?period=Q1%202024"
```

### HR Endpoints (API Key Required)
```bash
# Get employees by department
curl -H "X-API-Key: hr_12345abcde" "http://localhost:8000/hr/employees?department=Engineering"

# Get HR policies
curl -H "X-API-Key: hr_12345abcde" "http://localhost:8000/hr/policies?policy_type=Leave"

# Get payroll data
curl -H "X-API-Key: hr_12345abcde" "http://localhost:8000/hr/payroll?period=2024-01"
```

### IT Endpoints (API Key Required)
```bash
# Check system status
curl -H "X-API-Key: it_12345abcde" http://localhost:8000/it/status

# Create support ticket
curl -X POST -H "X-API-Key: it_12345abcde" -H "Content-Type: application/json" \
  -d '{"title": "Website issue", "description": "Homepage not loading", "priority": "high"}' \
  http://localhost:8000/it/support/ticket

# Reset password
curl -X POST -H "X-API-Key: it_12345abcde" -H "Content-Type: application/json" \
  -d '{"username": "johndoe"}' \
  http://localhost:8000/it/auth/password/reset
```

## Project Structure

```
dummy-json-server/
├── main.py                 # Main FastAPI application
├── routers/               # API route handlers
│   ├── __init__.py
│   ├── users.py          # User management endpoints
│   ├── products.py       # Product catalog endpoints
│   ├── orders.py         # Order management endpoints
│   ├── financial.py      # Financial data endpoints
│   ├── hr.py            # Human resources endpoints
│   └── it.py            # IT management endpoints
├── data/                 # JSON data storage
│   ├── users.json
│   ├── products.json
│   ├── orders.json
│   ├── financial.json
│   ├── hr.json
│   └── it.json
├── requirements.txt      # Python dependencies
└── README.md           # This file
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Adding New Endpoints

1. **Create a new router file** in `routers/` directory
2. **Define your endpoints** with proper authentication and validation
3. **Include the router** in `main.py`
4. **Add sample data** in the corresponding JSON file in `data/` directory

Example for adding a new `inventory` router:
```python
# routers/inventory.py
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/items")
async def get_inventory_items():
    return {"message": "Inventory items"}
```

```python
# main.py (add this line)
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
```

## Data Customization

Edit the JSON files in the `data/` directory to customize the responses:

```json
// data/users.json
[
  {
    "id": 1,
    "name": "Custom User",
    "email": "custom@example.com",
    "role": "admin"
  }
]
```

The server will automatically use your custom data on next request.

## Configuration

### Environment Variables
```bash
export PORT=8002
export HOST=0.0.0.0
export DEBUG=true
```

### Running with Custom Settings
```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## Development

### Testing the API
```bash
# Test all endpoints
curl http://localhost:8000/

# Test with authentication
curl -H "X-API-Key: your_api_key" http://localhost:8000/your/endpoint
```

### Adding Authentication
The project uses simple API key authentication. For production use, consider implementing:

- JWT tokens
- OAuth2
- Database-based user authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the existing issues
3. Create a new issue with detailed information

## Performance Tips

- The server uses in-memory data storage for simplicity
- For production use, consider adding caching with Redis
- Implement database persistence for larger datasets
- Add rate limiting for public endpoints

---

**Note**: This is a dummy server for development and testing purposes. Do not use in production without proper security measures.