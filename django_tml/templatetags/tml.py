# encoding: UTF-8

from __future__ import absolute_import
from django.template import (Node, Variable, TemplateSyntaxError,
     Library)
from django.template.base import TokenParser, TOKEN_TEXT, TOKEN_VAR
from django.template.base import render_value_in_context
from django.template.defaulttags import token_kwargs
from django.utils import six, translation
import sys
from django.utils.translation.trans_real import trim_whitespace
from django_tml import Translator
from tml import legacy
from django.templatetags.i18n import BlockTranslateNode as BaseBlockTranslateNode
from .. import inline_translations
from tml.translation import Key
from tml.dictionary import TranslationIsNotExists

register = Library()

class BlockTranslateNode(BaseBlockTranslateNode):

    def __init__(self, extra_context, singular, plural, countervar, counter, description, trimmed, nowrap = False, legacy = False):
        """ Block for {% tr %} {% endtr %}
            extra_context (dict): block with params
            singular (string): label for singular
            plural (string): label for plural
            message_context (string): key description
            contervar (string): variable for counter
            trimmed (boolean): trim context
            nowrap (boolean): no not wrap result in <tml:label> for inline tranlation
            legacy (boolean): supports legacy e.c. allow {{name}} syntax in label and %(name)s syntax in response

        """
        self.extra_context = extra_context
        self.description = description
        self.singular = singular
        self.plural = plural
        self.countervar = countervar
        self.counter = counter
        self.trimmed = trimmed
        self.legacy = legacy
        self.nowrap = nowrap


    def render(self, data, nested=False):
        """ Render result """
        if self.description:
            description = self.description.resolve(data)
        else:
            description = ''
 
        custom_data = {}
        for var, val in list(self.extra_context.items()):
            custom_data[var] = val.resolve(data)
        data.update(custom_data)

        if self.plural and self.countervar and self.counter:
            # Plural:
            count = self.counter.resolve(data)
            data[self.countervar] = count
            if count == 1:
                label, void = self.render_token_list(self.singular)
            else:
                label, void = self.render_token_list(self.plural)
        else:
            label, void = self.render_token_list(self.singular)
        return self.translate(label, data, description)


    def translate(self, label, data, description):
        """ Translate label
            Args:
                label (string): translated label
                data (dict): user data
                description: description
            Returns:
                translated text, key, translated
        """
        context = Translator.instance().context
        try:
            translation = context.fetch(label, description)
            translated = True
        except TranslationIsNotExists:
            translation = context.fallback(label, description)
            translated = False

        return self.wrap_label(context.render(translation, data, {}),
                               translation.key,
                               translated)

    def wrap_label(self, text, key, translated):
        if self.nowrap:
            # nowrap flag is set
            return text
        return inline_translations.wrap_string(text, key, translated)
 


class LegacyBlockTranlationNode(BlockTranslateNode):
    """ Tranlation with back support """
    def translate(self, label, data, description):
        """ Fetch tranlation
            Args:
                label (string): label in format for sprintf
                description (string)
            Return:
                tranlation
        """
        context = Translator.instance().context
        translation = legacy.fetch(context, label, description)
        # Execute in legacy mode with %(token)s support
        return legacy.execute(translation, data, {})


@register.tag("tr")
def do_block_translate(parser, token, legacy = False):
    """
    This will translate a block of text with parameters.

    Usage::

        {% tr with bar=foo|filter boo=baz|filter %}
        This is {{ bar }} and {{ boo }}.
        {% endtr %}

    Additionally, this supports pluralization::

        {% tr count count=var|length %}
        There is {{ count }} object.
        {% plural %}
        There are {{ count }} objects.
        {% endtr %}

    This is much like ngettext, only in template syntax.

    The "var as value" legacy format is still supported::

        {% tr with foo|filter as bar and baz|filter as boo %}
        {% tr count var|length as count %}

    Contextual translations are supported::

        {% tr with bar=foo|filter context "greeting" %}
            This is {{ bar }}.
        {% endtr %}

    This is equivalent to calling pgettext/npgettext instead of
    (u)gettext/(u)ngettext.
    """
    bits = token.split_contents()
    close_token = 'endblocktrans' if legacy else 'endtr'
    options = {}
    remaining_bits = bits[1:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise TemplateSyntaxError('The %r option was specified more '
                                      'than once.' % option)
        if option == 'with':
            value = token_kwargs(remaining_bits, parser, support_legacy=True)
            if not value:
                raise TemplateSyntaxError('"with" in %r tag needs at least '
                                          'one keyword argument.' % bits[0])
        elif option == 'count':
            value = token_kwargs(remaining_bits, parser, support_legacy=True)
            if len(value) != 1:
                raise TemplateSyntaxError('"count" in %r tag expected exactly '
                                          'one keyword argument.' % bits[0])
        elif option == "context":
            try:
                value = remaining_bits.pop(0)
                value = parser.compile_filter(value)
            except Exception:
                msg = (
                    '"context" in %r tag expected '
                    'exactly one argument.') % bits[0]
                six.reraise(TemplateSyntaxError, TemplateSyntaxError(msg), sys.exc_info()[2])
        elif option == "trimmed":
            value = True
        elif option == "nowrap":
            value = True
        else:
            raise TemplateSyntaxError('Unknown argument for %r tag: %r.' %
                                      (bits[0], option))
        options[option] = value

    if 'count' in options:
        countervar, counter = list(six.iteritems(options['count']))[0]
    else:
        countervar, counter = None, None
    if 'context' in options:
        message_context = options['context']
    else:
        message_context = None
    extra_context = options.get('with', {})

    trimmed = options.get("trimmed", False)

    singular = []
    plural = []
    while parser.tokens:
        token = parser.next_token()
        if token.token_type in (TOKEN_VAR, TOKEN_TEXT):
            singular.append(token)
        else:
            break
    if countervar and counter:
        if token.contents.strip() != 'plural':
            raise TemplateSyntaxError("'tr' doesn't allow other block tags inside it")
        while parser.tokens:
            token = parser.next_token()
            if token.token_type in (TOKEN_VAR, TOKEN_TEXT):
                plural.append(token)
            else:
                break
    if token.contents.strip() != close_token:
        raise TemplateSyntaxError("'tr' doesn't allow other block tags (seen %r) inside it" % token.contents)

    cls = LegacyBlockTranlationNode if legacy else BlockTranslateNode
    return cls(extra_context, singular, plural, countervar,
                              counter, message_context, trimmed = trimmed, legacy = legacy, nowrap = options.get('nowrap', False))

@register.tag("blocktrans")
def do_block_translate_legacy(parser, token):
    return do_block_translate(parser, token, True)

