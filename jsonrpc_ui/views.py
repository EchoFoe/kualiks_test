import json
from typing import Dict, Any

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from jsonrpc_app.rpc_client import call_jsonrpc_method


class JsonRpcView(View):
    """
    Класс-представление для обработки JSON-RPC запросов.

    Attrs:
       - template_name (str): Имя шаблона для отображения веб-интерфейса JSON-RPC.
    """

    template_name: str = 'jsonrpc_ui/index.html'

    def get(self, request, *args, **kwargs) -> render:
        """
        Обработчик GET запроса, отображает веб-интерфейс JSON-RPC.

        Args:
            request (HttpRequest): Объект запроса Django.

        Returns:
            render: Отрисованный HTTP ответ с шаблоном.
        """
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs) -> JsonResponse:
        """
        Обработчик POST запроса JSON-RPC метода.

        Args:
            request (HttpRequest): Объект POST запроса Django.

        Returns:
            JsonResponse: JSON ответ на POST запрос с результатами вызова JSON-RPC метода.
        """
        method: str = request.POST.get('method', '')
        params: str = request.POST.get('params', '{}')

        try:
            params_dict: Dict[str, Any] = json.loads(params)
        except json.JSONDecodeError:
            params_dict: Dict[str, Any] = {}

        response: Dict[str, Any] = call_jsonrpc_method(method, params_dict)

        return JsonResponse(response)
