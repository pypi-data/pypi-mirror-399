from django.conf import settings
from hrenpack.framework.django import get_view_base_template


# def base_template_context(request):
#     view = request.resolver_match.func
#     view = getattr(view, 'view_class', view)
#     return dict(base_template=get_view_base_template(view))


# def base_template_context(request):
#     try:
#         view = request.resolver_match.func
#         view = getattr(view, 'view_class', view)
#         base_template = get_view_base_template(view)
#         if not base_template:
#             raise ValueError("Empty template name")
#         return {'base_template': base_template}
#     except Exception as e:
#         # Логируйте ошибку для отладки
#         import logging
#         logging.getLogger(__name__).error(f"Error in base_template_context: {e}")
#         return {'base_template': 'empty.html'}  # Значение по умолчанию


def protocol_and_domain(request):
    return dict(protocol='https' if request.is_secure() else 'http', domain=request.get_host())
