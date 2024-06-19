from typing import Optional, Dict, Any

import json
import requests
import tempfile

from django.conf import settings


def call_jsonrpc_method(method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Выполняет вызов метода jsonprc с использованием двусторонней аутентификации SSL.

    Args:
        method (str): Метод jsonprc, который нужно вызвать.
        params (Optional[Dict[str, Any]], optional): Параметры для передачи методу. По умолчанию None.

    Returns:
        Dict[str, Any]: Ответ от сервера в формате jsonprc.

    Raises:
        requests.exceptions.RequestException: Возникает при ошибке выполнения HTTP-запроса.

    """
    url: str = settings.TEST_API_URL
    headers: Dict[str, str] = {'Content-Type': 'application/json'}

    payload: Dict[str, Any] = {
        'jsonrpc': '2.0',
        'method': method,
        'params': params or {},
        'id': 1
    }

    try:
        with tempfile.NamedTemporaryFile(delete=False) as cert_file, \
                tempfile.NamedTemporaryFile(delete=False) as key_file:

            cert_file.write(settings.CLIENT_CERT.encode('utf-8'))
            key_file.write(settings.CLIENT_KEY.encode('utf-8'))
            cert_file.flush()
            key_file.flush()

            response: requests.Response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                cert=(cert_file.name, key_file.name),
                verify=True
            )
            response.raise_for_status()

            json_response: Dict[str, Any] = response.json()
            if 'error' in json_response:
                return json_response

            return json_response
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}
