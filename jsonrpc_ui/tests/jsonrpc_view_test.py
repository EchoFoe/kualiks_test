import json
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.http import JsonResponse, HttpResponse
from django.urls import reverse

from jsonrpc_ui.views import JsonRpcView


class JsonRpcViewTestCase(TestCase):
    """
    Тестовый класс для проверки представления JsonRpcView.

    Attrs:
        - view (JsonRpcView): Экземпляр представления для тестирования.
        - factory (RequestFactory): Фабрика для создания запросов.
    """

    def setUp(self) -> None:
        """
        Устанавливает исходные данные для тестов.
        """
        self.view: JsonRpcView = JsonRpcView()
        self.factory: RequestFactory = RequestFactory()

    def test_get_method(self) -> None:
        """
        Тестирует обработчик GET запросов.
        """
        request: HttpResponse = self.factory.get('/jsonrpc/')
        response: HttpResponse = self.view.get(request)

        self.assertEqual(response.status_code, 200)

    @patch('jsonrpc_ui.views.call_jsonrpc_method')
    def test_post_method_success(self, mock_call_jsonrpc_method: MagicMock) -> None:
        """
        Тестирует успешный вызов jsonprc метода через POST запрос.

        Args:
            mock_call_jsonrpc_method (MagicMock): Мок объекта вызова jsonprc метода.
        """
        mock_call_jsonrpc_method.return_value = {
            'result': {
                '_data': {
                    'user': {
                        'id': 1,
                        'first_name': 'Test',
                        'email': 'test@example.com',
                        'is_active': True
                    }
                }
            }
        }

        url: str = reverse('jsonrpc_view')
        data: Dict[str, str] = {'method': 'auth.check', 'params': '{}'}
        request: HttpResponse = self.factory.post(url, data=data)

        response: JsonResponse = self.view.post(request)

        self.assertEqual(response.status_code, 200)
        json_response: Dict[str, Any] = json.loads(response.content.decode('utf-8'))
        self.assertIn('result', json_response)

        user_data: Dict[str, Any] = json_response['result']['_data']['user']
        self.assertEqual(user_data['id'], 1)
        self.assertEqual(user_data['first_name'], 'Test')
        self.assertEqual(user_data['email'], 'test@example.com')
        self.assertEqual(user_data['is_active'], True)

    @patch('jsonrpc_ui.views.call_jsonrpc_method')
    def test_post_method_error(self, mock_call_jsonrpc_method: MagicMock) -> None:
        """
        Тестирует обработку ошибки jsonprc метода через POST запрос.

        Args:
            mock_call_jsonrpc_method (MagicMock): Мок объекта вызова jsonprc метода.
        """
        mock_call_jsonrpc_method.return_value = {'error': 'Фейковые SSL'}

        url: str = reverse('jsonrpc_view')
        data: Dict[str, str] = {'method': 'auth.check', 'params': '{}'}
        request: HttpResponse = self.factory.post(url, data=data)

        response: JsonResponse = self.view.post(request)

        self.assertEqual(response.status_code, 200)
        json_response: Dict[str, Any] = json.loads(response.content.decode('utf-8'))
        self.assertIn('error', json_response)
        self.assertEqual(json_response['error'], 'Фейковые SSL')
