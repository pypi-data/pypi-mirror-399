from django.template import Library
from django.template.base import Node, TemplateSyntaxError

register = Library()


class ConditionBlockNode(Node):
    def __init__(self, conditions, nodelist_else=None, variable_name=None):
        self.conditions = conditions  # список кортежей (условие, nodelist)
        self.nodelist_else = nodelist_else
        self.variable_name = variable_name

    def render(self, context):
        # Проверяем условия по порядку
        for condition, nodelist in self.conditions:
            if condition.eval(context):
                result = nodelist.render(context)
                if self.variable_name:
                    context[self.variable_name] = result
                    return ''
                return result

        # Если ни одно условие не выполнилось, используем else
        if self.nodelist_else:
            result = self.nodelist_else.render(context)
            if self.variable_name:
                context[self.variable_name] = result
                return ''
            return result

        if self.variable_name:
            context[self.variable_name] = ''
            return ''

        return ''


@register.tag(name='conditionblock')
def do_conditionblock(parser, token):
    """
    Синтаксис:
    {% conditionblock condition as var_name %}
        содержимое при истинном условии
    {% elif condition %}
        содержимое при истинном elif
    {% else %}
        содержимое при всех ложных условиях
    {% endconditionblock %}
    """
    bits = token.split_contents()
    variable_name = None

    # Обрабатываем часть 'as variable_name'
    if len(bits) > 2 and bits[-2] == 'as':
        variable_name = bits[-1]
        condition = parser.compile_filter(' '.join(bits[1:-2]))
    elif len(bits) > 1:
        condition = parser.compile_filter(' '.join(bits[1:]))
    else:
        raise TemplateSyntaxError("'conditionblock' требует хотя бы одного аргумента")

    conditions = [(condition, parser.parse(('elif', 'else', 'endconditionblock')))]

    token = parser.next_token()

    # Обрабатываем все elif
    while token.contents.startswith('elif'):
        condition = parser.compile_filter(token.contents[4:].strip())
        nodelist = parser.parse(('elif', 'else', 'endconditionblock'))
        conditions.append((condition, nodelist))
        token = parser.next_token()

    # Обрабатываем else, если есть
    nodelist_else = None
    if token.contents == 'else':
        nodelist_else = parser.parse(('endconditionblock',))
        token = parser.next_token()

    if token.contents != 'endconditionblock':
        raise TemplateSyntaxError("Ожидается закрывающий тег 'endconditionblock'")

    return ConditionBlockNode(conditions, nodelist_else, variable_name)


class VarBlockNode(Node):
    def __init__(self, nodelist, variable_name=None):
        self.nodelist = nodelist
        self.variable_name = variable_name

    def render(self, context):
        content = self.nodelist.render(context)

        # Если указано имя переменной, сохраняем результат в контекст
        if self.variable_name:
            context[self.variable_name] = content
            return ''

        return content


@register.tag(name='varblock')
def do_varblock(parser, token):
    """
        Тег с синтаксисом:
        {% tag as variable_name %}
            содержимое
        {% endtag %}
        """
    bits = token.split_contents()
    variable_name = None

    if len(bits) > 1:
        if bits[1] != 'as':
            raise TemplateSyntaxError("Ожидается 'as' после имени тега")
        if len(bits) < 3:
            raise TemplateSyntaxError("Необходимо указать имя переменной после 'as'")
        variable_name = bits[2]

    nodelist = parser.parse(('endtag',))
    parser.delete_first_token()

    return VarBlockNode(nodelist, variable_name)
