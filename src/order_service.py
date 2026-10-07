# order_service.py
from fastapi import FastAPI, HTTPException
import httpx
import os

app = FastAPI()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")

orders_db = []

class OrderLogic:
    async def create_order(self, user_id: str, item_name: str):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{USER_SERVICE_URL}/users/{user_id}", timeout=2.0)
                
                if resp.status_code == 404:
                    raise ValueError("User does not exist")
                elif resp.status_code != 200:
                    raise ConnectionError("User service error")
                
                user_data = resp.json()
                
                new_order = {
                    "order_id": len(orders_db) + 1,
                    "user_name": user_data["name"],
                    "item": item_name,
                    "status": "CREATED"
                }
                orders_db.append(new_order)
                return new_order
                
        except httpx.ConnectError:
             raise ConnectionError("User service unreachable")
        except httpx.TimeoutException:
             raise TimeoutError("User service timed out")

logic = OrderLogic()

@app.post("/orders")
async def create_order_endpoint(payload: dict):
    user_id = payload.get("user_id")
    item = payload.get("item")
    
    if not user_id or not item:
        raise HTTPException(status_code=400, detail="Missing fields")

    try:
        result = await logic.create_order(user_id, item)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))