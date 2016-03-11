# encoding: UTF-8

from __future__ import absolute_import
import re
from django.template import (Node, Variable, TemplateSyntaxError,
     Library)
from django.template.base import TOKEN_TEXT, TOKEN_VAR
try:
    from django.template.base import TokenParser
except:
    from django.template.base import Parser as TokenParser
from django.template.base import render_value_in_context, Token, Lexer
from django.template import Template
from django.template.defaulttags import token_kwargs
from django.utils import six, translation
import sys
from django.utils.translation.trans_real import trim_whitespace
from django.utils.safestring import SafeData, mark_safe
from django_tml import Translation
from tml import legacy
from django.templatetags.i18n import BlockTranslateNode as BaseBlockTranslateNode, TranslateNode as BaseTranslateNode
from tml.translation import Key
from tml.dictionary import TranslationIsNotExists
from tml.session_vars import get_current_translator
from tml.logger import LoggerMixin
from tml.decoration.parser import ParseError as DecorationParseError
from tml.token import InvalidTokenSyntax
from tml.rules.engine import Error as EngineError
from tml.rules.options import Error as OptionsError
from tml.rules.parser import ParseError
from tml.decoration import AttributeIsNotSet, UnsupportedTag

register = Library()


RE_VARIABLE = r'.*\{\{\s(\w+)\s\}\}.*'


def handle_tml_exception(exc, silent=True):
    if isinstance(exc, (ParseError, InvalidTokenSyntax, DecorationParseError, UnsupportedTag, AttributeIsNotSet, EngineError, OptionsError)):
        msg = "Exception `%s` is raised with message `%s`. For details see stack trace." % (exc.__class__.__name__, str(exc))
        if not silent: # useful for debugging
            six.reraise(TemplateSyntaxError, TemplateSyntaxError(msg), sys.exc_info()[2])
        return ''


class TmlStringMixin(object):

    def is_translated_string(self, error):
        return not isinstance(error, TranslationIsNotExists)

    def wrap_label(self, text, key, translated):
        if self.nowrap:
            # nowrap flag is set
            return text
        return self.wrap_string(text, key, translated)

    def wrap_string(self, text, key, translated):
        translator = get_current_translator()
        if not translator or not translator.is_inline():
            return text
        # @todo: 1. tml_pending must handle: if ongoing to API
        # 2. if translation came and has flag (attribute) `locked` => tml_locked
        # 3. see ruby decorators/html.rb
        class_name = 'tml_translated' if translated else 'tml_not_translated'
        return six.u('<tml:label class="tml_translatable %(class_name)s" data-translation_key="%(key)s" data-target_locale="%(locale)s">%(text)s</tml:label>') % ({'key':key.key, 'text':text, 'class_name': class_name, 'locale': Translation.instance().locale})


class TranslateNode(BaseTranslateNode, TmlStringMixin, LoggerMixin):
    def __init__(self, filter_expression, nowrap = False, asvar=None, message_context=None):
        """ Tag for {% trs %}
            filter_expression (string): translateable string expr
            asvar (boolean): render or store in context for reuse
            message_context (string): key description
            nowrap (boolean): no not wrap result in <tml:label> for inline tranlation
        """
        self.asvar = asvar
        self.message_context = message_context
        self.filter_expression = filter_expression
        if isinstance(self.filter_expression.var, six.string_types):
            self.filter_expression.var = Variable("'%s'" %
                                                  self.filter_expression.var)
        self.nowrap = nowrap

    def render(self, context):
        output = self.filter_expression.resolve(context)
        if re.match(RE_VARIABLE, output):
            output = Template(output).render(context)
        description = ''
        if self.message_context:
            description = self.message_context.resolve(context)
        value = self.get_value(output, context)
        if not value:  # empty value
            return ''
        value = self.translate(value, description)
        if self.asvar:
            context[self.asvar] = value
            return ''
        else:
            return value

    def get_value(self, output, context):
        value = render_value_in_context(output, context)
        is_safe = isinstance(value, SafeData)
        # Restore percent signs. Percent signs in template text are doubled
        # so they are not interpreted as string format flags.
        value = value.replace('%%', '%')
        return mark_safe(value) if is_safe else value

    def translate(self, label, description):
        """ Translate label
            Args:
                label (string): translated label
                data (dict): user data
                description: description
            Returns:
                translated text, key, translated
        """
        try:
            key, trans_value, error = Translation.instance().tr(label, data={}, description=description, options={})
            translated = self.is_translated_string(error)
            return self.wrap_label(trans_value, key, translated)
        except Exception as e:
            self.exception(e)
            return handle_tml_exception(e)


class BlockTranslateNode(TmlStringMixin, BaseBlockTranslateNode, LoggerMixin):

    def __init__(self, extra_context, singular, plural, countervar, counter, description, trimmed, nowrap = False, legacy = False, asvar=None):
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
        self.asvar = asvar


    def render(self, context, nested=False):
        """ Render result """
        if self.description:
            description = self.description.resolve(context)
        else:
            description = ''

        custom_data = {}
        for var, val in list(self.extra_context.items()):
            custom_data[var] = val.resolve(context)
        context.update(custom_data)

        if self.plural and self.countervar and self.counter:
            # Plural:
            count = self.counter.resolve(context)
            context[self.countervar] = count
            if count == 1:
                label, void = self.render_token_list(self.singular)
            else:
                label, void = self.render_token_list(self.plural)
        else:
            label, void = self.render_token_list(self.singular)

        result = self.translate(label, context, description)
        if self.asvar:
            context[self.asvar] = result
            return ''
        else:
            return result


    def translate(self, label, data, description):
        """ Translate label
            Args:
                label (string): translated label
                data (dict): user data
                description: description
            Returns:
                translated text, key, translated
        """
        try:
            key, trans_value, error = Translation.instance().tr(label, data=data, description=description, options={})
            translated = self.is_translated_string(error)
            return self.wrap_label(trans_value, key, translated)
        except Exception as e:
            self.exception(e)
            return handle_tml_exception(e)


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
        try:
            _, trans_value, _ = Translation.instance().tr_legacy(label, data=data, description=description, options={})
            return trans_value   # we do not wrap here (todo: should think)
        except Exception as e:
            self.exception(e)
            return handle_tml_exception(e)


class TmlOptionsNode(Node):

    def __init__(self, nodelist, source=None, locale=None, language=None, **tml_options):
        self.nodelist = nodelist
        self.source = source
        self.target_locale = locale or language

    def render(self, context):
        with Translation.instance().with_block_options(
                source=self.source.resolve(context),
                target_locale=self.target_locale):
            output = self.nodelist.render(context)
        return output


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
        There is { count } object.
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
    {% troptions source=123 %}

    {% endtroptions %}
    """
    bits = token.split_contents()
    close_token = 'endblocktrans' if legacy else 'endtr'
    options = {}
    remaining_bits = bits[1:]
    asvar = None
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
        elif option == "asvar":
            try:
                value = remaining_bits.pop(0)
            except IndexError:
                msg = "No argument provided to the '%s' tag for the asvar option." % bits[0]
                six.reraise(TemplateSyntaxError, TemplateSyntaxError(msg), sys.exc_info()[2])
            asvar = value
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
                              counter, message_context, trimmed = trimmed, legacy = legacy, nowrap = options.get('nowrap', False), asvar=asvar)

@register.tag("blocktrans")
def do_block_translate_legacy(parser, token):
    return do_block_translate(parser, token, True)


@register.tag('trs')
def do_translate(parser, token):
    """This will mark a string for translation and will
    translate the string for the current language.

    Usage::

        {% trs "hello world" %}

    This will mark the string for translation so it will
    be handled by tml register backend and will run the string through the tml translation engine.

    You can use variables instead of constant strings
    to translate stuff you marked somewhere else::

    {% trs variable %}

    This will just try to translate the contents of
    the variable ``variable``. Make sure that the string
    in there is something that is in tml dashboard.

    It is possible to store the translated string into a variable::

        {% trs "this is a test" as var %}
        {{ var }}

    Contextual translations are also supported::

        {% trs "this is a test" context "greeting" %}

    This is equivalent to calling pgettext instead of (u)gettext."""
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument" % bits[0])
    message_string = parser.compile_filter(bits[1])
    remaining = bits[2:]

    noop = False
    asvar = None
    message_context = None
    seen = set()
    invalid_context = {'as', 'nowrap'}

    while remaining:
        option = remaining.pop(0)
        if option in seen:
            raise TemplateSyntaxError(
                "The '%s' option was specified more than once." % option,
            )
        elif option == 'context':
            try:
                value = remaining.pop(0)
            except IndexError:
                msg = "No argument provided to the '%s' tag for the context option." % bits[0]
                six.reraise(TemplateSyntaxError, TemplateSyntaxError(msg), sys.exc_info()[2])
            if value in invalid_context:
                raise TemplateSyntaxError(
                    "Invalid argument '%s' provided to the '%s' tag for the context option" % (value, bits[0]),
                )
            message_context = parser.compile_filter(value)
        elif option == 'as':
            try:
                value = remaining.pop(0)
            except IndexError:
                msg = "No argument provided to the '%s' tag for the as option." % bits[0]
                six.reraise(TemplateSyntaxError, TemplateSyntaxError(msg), sys.exc_info()[2])
            asvar = value
        elif option == 'nowrap':
            pass
        else:
            raise TemplateSyntaxError(
                "Unknown argument for '%s' tag: '%s'. The only options "
                "available are 'noop', 'context' \"xxx\", and 'as VAR'." % (
                    bits[0], option,
                )
            )
        seen.add(option)
    return TranslateNode(message_string, asvar=asvar, message_context=message_context, nowrap='nowrap' in seen)

@register.tag('tmlopts')
def do_tml_options(parser, token):
    """
    Enables a given tml options for this block.

    The ``timezone`` argument must be an instance of a ``tzinfo`` subclass, a
    time zone name, or ``None``. If is it a time zone name, pytz is required.
    If it is ``None``, the default time zone is used within the block.

    Sample usage::

        {% tmlopts with source="navigation" locale="ru" %}
            {% trs "hello world" %}
            {% tr with bar=foo|filter context "greeting" %}
                This is {{ bar }}.
            {% endtr %}
        {% endtmlopts %}

        {% tmlopts with source=var|filter language="en" %}
            ...
        {% endtmlopts %}
    """
    bits = token.split_contents()
    close_token = ('endtmlopts',)
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
        else:
            raise TemplateSyntaxError(
                "Unknown argument for '%s' tag: '%s'. The only options "
                "available are 'with' and 'as VAR'." % (
                    bits[0], option,
                )
            )

        options[option] = value

    tml_options = options.get('with', {})
    nodelist = parser.parse(close_token)
    parser.delete_first_token()
    return TmlOptionsNode(nodelist, **tml_options)


@register.tag('source')
def do_source_tag(parser, token):
    """
    Samle usage::

        {% source "navigation" %}
            ...
        {% endsource %}
    """
    close_token = ('endsource',)
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%r' statement takes one argument" % bits[0])
    source = parser.compile_filter(bits[1])
    nodelist = parser.parse(close_token)
    parser.delete_first_token()
    return TmlOptionsNode(nodelist, source=source)

@register.tag('trlocale')
def do_tr_locale(parser, token):
    """
    Samle usage::

        {% trlocale "en" %}
            ...
        {% endtrlocale %}
    """
    close_token = ('endtrlocale',)
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%r' statement takes one argument" % bits[0])
    target_locale = parser.compile_filter(bits[1])
    nodelist = parser.parse(close_token)
    parser.delete_first_token()
    return TmlOptionsNode(nodelist, locale=target_locale)
