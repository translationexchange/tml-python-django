from __future__ import absolute_import
# encoding: UTF-8
from ..utils import ts
from django.template import Node, Library
from django.template.loader import render_to_string
from ..translator import Translation
from tml.config import CONFIG
from tml import full_version
from json import dumps

register = Library()

class TmlInlineNode(Node):
    templates = []

    def render(self, data, nested=False):
        translation = Translation.instance()
        agent_config = translation.config.get('agent', {})
        agent_host = agent_config.get('host', 'https://tools.translationexchange.com/agent/stable/agent.min.js')
        if agent_config.get('cache', None):
            t = ts()
            t -= (t % agent_config['cache'])
            agent_host += "?ts=%s" % t
        agent_config['locale'] = translation.get_language()
        agent_config['source'] = tml_current_source
        agent_config['css'] = translation.application.css
        agent_config['sdk'] = full_version()
        languages = agent_config.setdefault('languages', [])
        for language in translation.languages:
            languages.append({
                'locale': language.locale,
                'native_name': language.native_name,
                'english_name': language.english_name,
                'flag_url': language.flag_url})
        data = {
            'agent_config': dumps(agent_config),
            'agent_host': agent_host,
            'application_key': application.key}
        return ''.join([
            render_to_string('django_tml/inline_translations/%s.html' % tpl, data) for tpl in self.templates])


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
