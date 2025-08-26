from fastapi import APIRouter, HTTPException
import json
import random
from pathlib import Path

router = APIRouter()

# Load user data
def load_user_data():
    data_file = Path("data/users.json")
    if not data_file.exists():
        # Default sample data
        default_data = [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "user"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "role": "admin"},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "role": "user"},
            {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "role": "moderator"},
            {"id": 5, "name": "Charlie Wilson", "email": "charlie@example.com", "role": "user"}
        ]
        data_file.parent.mkdir(exist_ok=True)
        data_file.write_text(json.dumps(default_data, indent=2))
        return default_data
    
    return json.loads(data_file.read_text())

@router.get("/random")
async def get_random_user():
    users = load_user_data()
    if not users:
        raise HTTPException(status_code=404, detail="No user data available")
    return random.choice(users)

@router.get("/all")
async def get_all_users():
    return load_user_data()

@router.get("/{user_id}")
async def get_user_by_id(user_id: int):
    users = load_user_data()
    for user in users:
        if user.get("id") == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")