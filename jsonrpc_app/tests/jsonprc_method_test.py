from typing import Dict, Any

import requests

from django.test import TestCase
from unittest.mock import patch, MagicMock


class JsonRpcMethodTest(TestCase):
    """
    Класс для тестирования вызовов jsonprc методов с использованием SSL.

    Attrs:
        - method (str): Метод jsonprc, который тестируется.
        - params (Dict[str, Any]): Параметры для передачи методу jsonprc.
        - cert_data (str): Фейковые данные сертификата для тестирования SSL.
        - key_data (str): Фейковые данные ключа для тестирования SSL.
    """

    def setUp(self) -> None:
        """
        Вводные данные сетапа для тестов jsonprc методов с SSL.
        """
        self.method: str = 'auth.check'
        self.params: Dict[str, Any] = {}
        self.cert_data: str = 'fake_cert_data'
        self.key_data: str = 'fake_key_data'

    def validate_successful_response(self, response: Dict[str, Any]) -> None:
        """
        Проверка успешного ответа метода jsonprc (тестируется некая сигнатура).
        """
        self.assertIsNotNone(response)
        self.assertIn('result', response)
        self.assertIn('_data', response['result'])

        user_data: Dict[str, Any] = response['result']['_data'].get('user', {})

        self.assertIn('id', user_data)
        self.assertIn('first_name', user_data)
        self.assertIn('email', user_data)
        self.assertIn('is_active', user_data)

    def test_call_jsonrpc_method_ssl_success(self) -> None:
        """
        Тест успешного вызова метода jsonprc с использованием SSL.
        """
        from jsonrpc_app.rpc_client import call_jsonrpc_method

        response: Dict[str, Any] = call_jsonrpc_method(self.method, self.params)
        self.validate_successful_response(response)
        print('Метод test_call_jsonrpc_method_ssl_success: ', response)

    def test_call_jsonrpc_method_ssl_error(self) -> None:
        """
        Тест обработки ошибки SSL при вызове метода jsonprc.
        """
        from jsonrpc_app.rpc_client import call_jsonrpc_method

        with patch('django.conf.settings.CLIENT_CERT', self.cert_data), \
             patch('django.conf.settings.CLIENT_KEY', self.key_data), \
             patch('requests.post') as mock_post:
            mock_post.side_effect = MagicMock(
                side_effect=requests.exceptions.SSLError('Фейковые SSL')
            )

            response: Dict[str, Any] = call_jsonrpc_method(self.method, self.params)

            self.assertIsNotNone(response)
            self.assertIn('error', response)
            self.assertEqual(response['error'], 'Фейковые SSL')
            print('Метод test_call_jsonrpc_method_ssl_error: ', response, "\n")
