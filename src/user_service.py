# user_service.py
from fastapi import FastAPI, HTTPException

app = FastAPI()

USERS_DB = {
    "1": {"id": "1", "name": "Alice"},
    "2": {"id": "2", "name": "Bob"}
}

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    return USERS_DB[user_id]