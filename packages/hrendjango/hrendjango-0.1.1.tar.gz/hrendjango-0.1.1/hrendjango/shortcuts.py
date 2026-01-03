from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseGone
from django.shortcuts import render as django_render


def render_construct(code: int):
    def render(request, template_name: str, context: dict, content_type=None, using=None):
        return django_render(request=request, template_name=template_name, context=context,
                             content_type=content_type, status=code, using=using)

    # return lambda request, template_name, context, content_type=None, using=None: django_render(
    #     request=request, template_name=template_name, context=context, content_type=content_type,
    #     status=code, using=using)
    return render


render_permanent_redirect = render_construct(301)
render_redirect = render_construct(302)
render_not_modified = render_construct(304)
render_bad_request = render_construct(400)
render_forbidden = render_construct(403)
render_not_found = render_construct(404)
render_gone = render_construct(410)
render_server_error = render_construct(500)
render_internal_server_error = render_construct(501)
render_not_implemented = render_construct(502)
render_bad_gate = render_construct(503)
