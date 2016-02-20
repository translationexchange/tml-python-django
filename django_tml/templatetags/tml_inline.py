afrom __future__ import absolute_import
# encoding: UTF-8
from django.template import Node, Library
from django.template.loader import render_to_string
from ..translator import Translator
from json import dumps

register = Library()

class TmlInlineNode(Node):
    templates = []
    def render(self, data, nested=False):
        translator = Translator.instance()
        data =  {'translator': translator,
                 'application': translator.context.application,
                 'language': translator.context.language,
                 'sources':dumps(translator.used_sources)}
        return ''.join([render_to_string('django_tml/inline_translations/%s.html' % tpl, data) for tpl in self.templates])


class TmlInlineHeader(TmlInlineNode):
    templates = ['header']

class TmlInlineFooter(TmlInlineNode):
    templates = ['footer']


@register.tag("tml_inline_header")
def tml_inline_header(parser, token):
    return TmlInlineHeader()

@register.tag("tml_inline_footer")
def tml_inline_footer(parser, token):
    return TmlInlineFooter()

@register.tag("activate_tml_inline")
def activate_tml_inline(parser, token):
    return TmlInlineHeader()
