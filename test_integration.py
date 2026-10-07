# test_integration.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
import httpx
from order_service import app as order_app

client = TestClient(order_app)

def make_mock_response(status_code, json_data=None):
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = status_code
    if json_data is not None:
        mock_resp.json.return_value = json_data
    return mock_resp

@pytest.fixture
def mock_http_client():
    # Патчим сам класс клиента, чтобы перехватывать все исходящие запросы
    with patch('order_service.httpx.AsyncClient') as MockAsyncClient:
        instance = MockAsyncClient.return_value.__aenter__.return_value
        yield instance

def test_create_order_success(mock_http_client):
    """Позитивный: Сервис заказов успешно получает данные пользователя"""
    # Имитируем ответ от User Service (порт 8001)
    mock_http_client.get.return_value = make_mock_response(200, {"id": "1", "name": "Alice"})

    response = client.post("/orders", json={"user_id": "1", "item": "Laptop"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_name"] == "Alice"
    assert data["item"] == "Laptop"
    
    # Проверяем, что был сделан запрос к правильному URL
    mock_http_client.get.assert_called_once_with("http://localhost:8001/users/1", timeout=2.0)

def test_create_order_user_not_found(mock_http_client):
    """Негативный: Пользователь не найден в User Service"""
    mock_http_client.get.return_value = make_mock_response(404)

    response = client.post("/orders", json={"user_id": "999", "item": "Phone"})
    
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]

def test_create_order_connection_error(mock_http_client):
    """Негативный: User Service недоступен (Connection Refused)"""
    # Выбрасываем исключение на уровне сетевого клиента
    mock_http_client.get.side_effect = httpx.ConnectError("Connection refused")

    response = client.post("/orders", json={"user_id": "1", "item": "Book"})
    
    assert response.status_code == 503
    assert "unreachable" in response.json()["detail"]

def test_create_order_timeout(mock_http_client):
    """Негативный: Таймаут ответа от User Service"""
    mock_http_client.get.side_effect = httpx.TimeoutException("Read timed out")

    response = client.post("/orders", json={"user_id": "1", "item": "Pen"})
    
    assert response.status_code == 504
    assert "timed out" in response.json()["detail"]

def test_create_order_bad_gateway(mock_http_client):
    """Негативный: User Service вернул 500 Internal Server Error"""
    mock_http_client.get.return_value = make_mock_response(500)

    response = client.post("/orders", json={"user_id": "1", "item": "Mouse"})
    
    assert response.status_code == 503
    assert "error" in response.json()["detail"].lower()