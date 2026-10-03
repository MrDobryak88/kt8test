import requests
from typing import Optional, Dict, Any

USERS_DB = {
    "1": {"id": "1", "name": "Alice", "email": "alice@test.com"},
    "2": {"id": "2", "name": "Bob", "email": "bob@test.com"}
}

class UserServiceLogic:
    @staticmethod
    def get_user(user_id: str) -> Optional[Dict[str, Any]]:
        return USERS_DB.get(user_id)

class OrderServiceLogic:
    USER_SERVICE_URL = "http://localhost:5001/users/"
    
    @staticmethod
    def fetch_user_from_external_service(user_id: str) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{OrderServiceLogic.USER_SERVICE_URL}{user_id}", timeout=2.0)
            if resp.status_code == 404:
                raise LookupError(f"User {user_id} not found")
            if resp.status_code != 200:
                raise ConnectionError(f"Bad status code: {resp.status_code}")
            return resp.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError("User Service is unreachable")
        except requests.exceptions.Timeout:
            raise TimeoutError("User Service timed out")

    @staticmethod
    def create_order(order_data: dict) -> dict:
        user_id = order_data.get('user_id')
        item = order_data.get('item')
        
        if not user_id or not item:
            raise ValueError("Missing required fields")

        user_info = OrderServiceLogic.fetch_user_from_external_service(user_id)
        
        new_order = {
            "id": 1, 
            "user_id": user_id,
            "user_name": user_info['name'],
            "item": item,
            "status": "created"
        }
        return new_order