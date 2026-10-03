import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Добавляем путь к проекту, чтобы импортировать services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services import OrderServiceLogic

class TestMicroservicesIntegration(unittest.TestCase):

    @patch('src.services.OrderServiceLogic.fetch_user_from_external_service')
    def test_create_order_success(self, mock_fetch):
        """Позитивный сценарий: Сервис заказов успешно получает данные пользователя"""
        mock_fetch.return_value = {"id": "1", "name": "Alice", "email": "a@t.com"}
        
        order_input = {"user_id": "1", "item": "Laptop"}
        result = OrderServiceLogic.create_order(order_input)
        
        self.assertEqual(result["user_name"], "Alice")
        self.assertEqual(result["item"], "Laptop")
        mock_fetch.assert_called_once_with("1")

    @patch('src.services.OrderServiceLogic.fetch_user_from_external_service')
    def test_create_order_user_not_found(self, mock_fetch):
        """Негативный сценарий: Пользователь не найден (404)"""
        from requests.exceptions import HTTPError
        # Имитируем ошибку, которую бросает наша логика внутри fetch... 
        # Но проще смоделировать исключение напрямую из уровня ниже, если бы оно пробрасывалось.
        # Здесь мы тестируем реакцию OrderService на ошибку от User Service.
        
        mock_fetch.side_effect = LookupError("User 999 not found")
        
        with self.assertRaises(LookupError):
            OrderServiceLogic.create_order({"user_id": "999", "item": "Phone"})

    @patch('src.services.OrderServiceLogic.fetch_user_from_external_service')
    def test_create_order_connection_error(self, mock_fetch):
        """Негативный сценарий: Сервис пользователей недоступен"""
        mock_fetch.side_effect = ConnectionError("Service Unreachable")
        
        with self.assertRaises(ConnectionError):
            OrderServiceLogic.create_order({"user_id": "1", "item": "Book"})

if __name__ == '__main__':
    unittest.main()