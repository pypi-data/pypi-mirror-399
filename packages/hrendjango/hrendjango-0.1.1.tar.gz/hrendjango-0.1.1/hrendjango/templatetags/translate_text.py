from typing import Optional
from deep_translator import GoogleTranslator as Translator
from django import template
from django.template import Library, Node
from django.conf import settings
from ..utils import translate_text as trans

register = Library()


@register.simple_tag
def translate_text(text, output_lang: Optional[str] = None, input_lang: Optional[str] = None):
    if input_lang is None:
        input_lang = 'en' if getattr(settings, 'HRENDJANGO_ENGLISH_INPUT_LANG', False) else 'auto'
    return trans(text, output_lang, input_lang)


@register.tag(name='translateblock')
def do_translateblock(parser, token):
    """
    Шаблонный тег для перевода текста через Google Translate.
    Синтаксис: {% translateblock 'source_lang' 'target_lang' %}текст{% endtranslateblock %}
    Пример: {% translateblock 'en' 'ru' %}Hello{% endtranslateblock %} → Привет
    """
    try:
        tag_name, input_lang, output_lang = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly two arguments: source and target language." % token.contents.split()[0]
        )

    nodelist = parser.parse(('endtranslateblock',))
    parser.delete_first_token()
    return TranslateBlockNode(nodelist, input_lang, output_lang)


class TranslateBlockNode(template.Node):
    def __init__(self, nodelist, input_lang, output_lang):
        self.nodelist = nodelist
        self.input_lang = input_lang.strip("'\"")
        self.output_lang = output_lang.strip("'\"")

    def render(self, context):
        text = self.nodelist.render(context).strip()
        translator = Translator()
        try:
            translated = translator.translate(
                text,
                src=self.input_lang,
                dest=self.output_lang
            )
            return translated.text
        except Exception as e:
            return f"Translation error: {str(e)}"
