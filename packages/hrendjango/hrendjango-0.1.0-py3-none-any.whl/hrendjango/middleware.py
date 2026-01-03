import importlib
from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from .constants import URLS_ROOT
from .exceptions import Http401

handler401 = getattr(URLS_ROOT, 'handler401', None)
handler405 = getattr(URLS_ROOT, 'handler405', None)


class HrendjangoMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, Http401):
            if handler401:
                return handler401(request)
            return HttpResponse("<h1>401 Unauthorized</h1>", status=401)

    def process_request(self, request):
        request.user_ip = request.META['REMOTE_ADDR']
        request.user_user_agent = request.META['HTTP_USER_AGENT']

    def process_response(self, request, response):
        if response.get('Content-Type', '').startswith('text/html'):
            favicon_url = '/static/favicon.png'  # Укажите путь к вашему favicon
            favicon_tag = f'    <link rel="icon" href="{favicon_url}">'
            response.content = response.content.replace(b'</head>', f'{favicon_tag}</head>'.encode('utf-8'))
        return response
