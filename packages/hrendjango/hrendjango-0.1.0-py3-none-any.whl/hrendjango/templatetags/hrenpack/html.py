from typing import Optional
from django.http import HttpRequest
from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.inclusion_tag('hrendjango/includes/form_context.html', takes_context=True)
def form_context(context, button_text: Optional[str] = None, button_class: Optional[str] = None, div_mode: bool = False,
                 br_post: bool = True, colon_post: bool = True, form=None, mode: str = 'normal', **kwargs):
    if form is None:
        form = context['form']
    if button_class is None:
        button_class = 'btn btn-hren'
    return {'form': form, 'button_text': button_text, 'br_post': br_post, 'fc_mode': mode,
            'colon_post': colon_post, 'button_class': button_class, 'div_mode': div_mode, **kwargs}


@register.simple_tag
def get_condition(condition: bool, true='', false=''):
    return true if condition else false


@register.simple_tag
def user_full_name(user):
    return user.get_full_name()


@register.simple_tag(takes_context=True)
def current_user_full_name(context):
    user = context['user']
    if user.is_authenticated:
        return user_full_name(user)


@register.inclusion_tag('system/includes/account.html', takes_context=True)
def account_content(context):
    context['name'] = current_user_full_name(context)
    return context


@register.simple_tag
def crutch():
    return mark_safe('<p style="color: transparent">.</p>')


@register.simple_tag
def html_text(text: str):
    return mark_safe(text)


@register.simple_tag
def simple_text(text: str):
    return text


@register.simple_tag
def var(arg):
    return arg


@register.simple_tag(takes_context=True)
def current_page(context):
    return context['request'].path


"""
@register.tag(name='varblock')
def do_varblock(parser, token):
    bits = token.split_contents()
    if len(bits) == 4 and bits[2] == 'as':
        # Если используется синтаксис {% mytag as variable %}
        nodelist = parser.parse(('endvarblock',))
        parser.delete_first_token()  # Удаляем {% endmytag %} из потока
        return VarBlockNode(nodelist, bits[3])
    elif len(bits) == 1:
        # Если используется обычный синтаксис {% mytag %}
        nodelist = parser.parse(('endvarblock',))
        parser.delete_first_token()
        return VarBlockNode(nodelist)
    else:
        register.raise_block_tag_with_as_error('varblock')


class VarBlockNode(Node):
    def __init__(self, nodelist, variable_name=None):
        self.nodelist = nodelist
        self.variable_name = variable_name

    def render(self, context):
        output = self.nodelist.render(context)
        if self.variable_name:
            context[self.variable_name] = output
            return ''  # Возвращаем пустую строку, так как результат сохранён в переменную
        else:
            return output
"""
