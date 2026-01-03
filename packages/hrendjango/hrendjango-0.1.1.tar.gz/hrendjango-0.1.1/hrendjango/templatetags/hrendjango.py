from django.template import Library
from django.templatetags.static import static

register = Library()
STYLES = {'hrendjango.css'}
SCRIPTS = {'hrendjango.js'}


@register.inclusion_tag('hrendjango/includes/init_styles.html')
def hrendjango_init_styles():
    return dict(styles=[static('hrendjango/css/' + css) for css in STYLES])


@register.inclusion_tag('hrendjango/includes/init_scripts.html')
def hrendjango_init_scripts():
    return dict(scripts=[static('hrendjango/js/' + js) for js in SCRIPTS])


@register.inclusion_tag('hrendjango/includes/init.html')
def hrendjango_init(styles=None, scripts=None):
    if styles is not None and scripts is not None:
        return dict(styles=styles, scripts=scripts)
    return dict(
        styles=(static('hrendjango/css/' + css for css in STYLES)),
        scripts=(static('hrendjango/js/' + js for js in SCRIPTS))
    )
