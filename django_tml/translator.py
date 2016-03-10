from __future__ import absolute_import
# encoding: UTF-8
import six
from types import FunctionType
from django.conf import settings as django_settings
from django.utils.translation.trans_real import to_locale, templatize, deactivate_all, parse_accept_lang_header, language_code_re, language_code_prefix_re
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.module_loading import import_string
from tml import configure, build_context
from tml.application import Application
from tml import Key
from tml.translation import TranslationOption, OptionIsNotFound
from tml.legacy import text_to_sprintf, suggest_label
from tml.api.client import Client
from tml.api.snapshot import open_snapshot
from tml.render import RenderEngine
from tml.logger import LoggerMixin
from .tml_cookies import TmlCookieHandler

__author__ = 'a@toukmanov.ru, xepa4ep'


def to_str(fn):
    def tmp(*args, **kwargs):
        return six.text_type(fn(*args, **kwargs))
    return tmp

def fallback_locale(locale):
    exploded = locale.split('-')
    if 2==len(exploded):
        return exploded[0]
    else:
        return None


class Translation(LoggerMixin):
    """ Basic translation class """
    _instance = None

    @classmethod
    def instance(cls, tml_settings=None):
        """ Singletone
            Returns:
                Translation
        """
        if cls._instance is None:
            cls._instance = cls(tml_settings or getattr(django_settings, 'TML', {}))
        return cls._instance

    def __init__(self, tml_settings):
        self.config = None
        self.locale = None
        self.source = None
        self._context = None
        self._supported_locales = None
        self._client = None
        self.access_token = None
        self.translator = None
        self.init(tml_settings)
        LoggerMixin.__init__(self)

    def init(self, tml_settings):
        self.config = configure(**tml_settings)
        self._build_preprocessors()

    @property
    def application(self):
        return self.context.application

    @property
    def application_key(self):
        return self.config.application_key()

    @property
    def languages(self):
        return self.application.languages

    def _build_preprocessors(self):
        """ Build translation preprocessors defined at TML_DATA_PREPROCESSORS """
        for include in self.config.get('data_preprocessors', []):
            RenderEngine.data_preprocessors.append(import_string(include))

        for include in self.config.get('env_generators', []):
            RenderEngine.env_generators.append(import_string(include))


    def build_context(self):
        """ Build context instance for locale
            Args:
                locale (str): locale name (en, ru)
            Returns:
                Context
        """
        return build_context(locale=self.locale,
                             source=self.source,  # todo:
                             client=self.build_client(self.access_token),
                             use_snapshot=self.use_snapshot,
                             translator=self.translator)

    @property
    def client(self):
        """ API client property (overrided in unit-tests)
            Returns:
                Client
        """
        return self.context.client

    def build_client(self, access_token):
        token = access_token or self.config.application.get('access_token', None)
        if 'api_client' in self.config:
            # Custom client:
            custom_client = self.config['api_client']
            if type(custom_client) is FunctionType:
                # factory function:
                return custom_client(key=self.application_key, access_token=token)
            elif custom_client is str:
                # full factory function or class name: path.to.module.function_name
                custom_client_import = '.'.split(custom_client)
                module = __import__('.'.join(custom_client[0, -1]))
                return getattr(module, custom_client[-1])(key=self.application_key, access_token=token)
            elif custom_client is object:
                # custom client as is:
                return custom_client
        return Client(key=self.application_key, access_token=token)

    @property
    def use_snapshot(self):
        cache = self.config.get('cache', {})
        return cache.get('adapter', None) == 'file' and cache.get('enabled', False) and self.config['environment'] == 'test'

    @property
    def context(self):
        """ Current context cached property
            Returns:
                Context
        """
        if self._context is None:
            self._context = self.build_context()

        return self._context

    def set_access_token(self, token):
        self.access_token = token
        return self

    def set_translator(self, translator):
        self.translator = translator
        return self

    def get_language(self):
        """ getter to current language """
        return self.locale or django_settings.LANGUAGE_CODE

    def activate(self, locale):
        """ Activate selected language
            Args:
                locale (string): selected locale
        """
        self.locale = locale
        self.reset_context()

    def activate_tml(self, source, access_token=None, translator=None, locale=None):
        if access_token:
            self.set_access_token(access_token)
        if translator:
            self.set_translator(translator)
        self.activate_source(source)
        if locale:
            self.activate(locale)

    def _use_source(self, source):
        self.source = source
        self.reset_context()

    def activate_source(self, source):
        """ Get source
            Args:
                source (string): source code
        """
        self._use_source(source)
        return self

    def deactivate_source(self):
        """ Deactivate source """
        self.activate_source(None)

    def reset_context(self):
        if self._context:
            self._context.deactivate()
        self._context = None

    def deactivate(self):
        """ Use default locole """
        self.locale = None
        self.reset_context()

    def gettext_noop(self, message):
        return message

    @to_str
    def gettext(self, message):
        return self.ugettext(message)

    @to_str
    def ngettext(self, singular, plural, number):
        return self.ungettext(singular, plural, number)

    def ugettext(self, message):
        return self.translate(message)

    def ungettext(self, singular, plural, number):
        if number == 1:
            return self.translate(singular, {'number': number})
        else:
            return self.translate(plural, {'number': number})

    @to_str
    def pgettext(self, context, message):
        return self.translate(message, description = context)

    @to_str
    def npgettext(self, context, singular, plural, number):
        if number == 1:
            return self.translate(singular, {'number': number}, context)
        else:
            return self.translate(plural, {'number': number}, context)

    def translate(self, label, data={}, description = None):
        """ Translate label """
        language = self.context.language
        key = Key(
            label=suggest_label(label),
            description=description,
            language=language)
        # fetch translation for key:
        translation = self.context.build_dict(language).translate(key)
        # prepare data for tranlation (apply env first):
        data = self.context.prepare_data(data)
        # fetch option depends env:
        try:
            option = translation.fetch_option(data, {})
        except OptionIsNotFound:
            try:
                option = self.context.fallback(label, description).fetch_option(data, {})
            except OptionIsNotFound:
                # Use label if tranlation fault:
                option = TranslationOption(label = label, language= language)

        # convert {name} -> %(name)s
        return text_to_sprintf(option.label, self.context.language)


    def get_language_bidi(self):
        return self.context.language.right_to_left

    def check_for_language(self, lang_code):
        """ Check is language supported by application
            Args:
                string lang_code
            Returns:
                boolean
        """
        return lang_code in self.supported_locales

    @property
    def supported_locales(self):
        if self._supported_locales is None:
            self._supported_locales = [str(locale) for locale in self.application.supported_locales]
        return self._supported_locales


    def to_locale(self, language):
        return to_locale(language)

    def get_language_from_request(self, request, check_path=False):
        """
        Analyzes the request to find what language the user wants the system to
        show. Only languages listed in settings.LANGUAGES are taken into account.
        If the user requests a sublanguage where we have a main language, we send
        out the main language.

        If check_path is True, the URL path prefix will be checked for a language
        code, otherwise this is skipped for backwards compatibility.
        """
        if check_path:
            lang_code = self.get_language_from_path(request.path_info)
            if lang_code is not None:
                return lang_code

        if hasattr(request, 'session'):
            # for backwards compatibility django_language is also checked (remove in 1.8)
            lang_code = request.session.get(LANGUAGE_SESSION_KEY, request.session.get('django_language'))
            if lang_code is not None:
                return lang_code

        cookie_handler = TmlCookieHandler(request, self.application_key)
        lang_code = cookie_handler.tml_locale
        if lang_code is not None:
            return lang_code

        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        for accept_lang, unused in parse_accept_lang_header(accept):
            if accept_lang == '*':
                break
            if not language_code_re.search(accept_lang):
                continue
            if lang_code is not None:
                return accept_lang

        return self.context.application.default_locale

    def get_language_from_path(self, path, strict=False):
        """
        Returns the language-code if there is a valid language-code
        found in the `path`.

        If `strict` is False (the default), the function will look for an alternative
        country-specific variant when the currently checked is not found.
        """
        regex_match = language_code_prefix_re.match(path)
        if not regex_match:
            return None
        lang_code = regex_match.group(1)
        try:
            return self.get_supported_language_variant(lang_code, strict=strict)
        except LookupError:
            return None


    def get_supported_language_variant(self, lang_code, strict=False):
        """
        Returns the language-code that's listed in supported languages, possibly
        selecting a more generic variant. Raises LookupError if nothing found.

        If `strict` is False (the default), the function will look for an alternative
        country-specific variant when the currently checked is not found.

        lru_cache should have a maxsize to prevent from memory exhaustion attacks,
        as the provided language codes are taken from the HTTP request. See also
        <https://www.djangoproject.com/weblog/2007/oct/26/security-fix/>.
        """
        _supported = self.supported_locales
        if lang_code:
            # if fr-ca is not supported, try fr.
            generic_lang_code = lang_code.split('-')[0]
            for code in (lang_code, generic_lang_code):
                if self.check_for_language(code):
                    return code
            if not strict:
                # if fr-fr is not supported, try fr-ca.
                for supported_code in _supported:
                    if supported_code.startswith(generic_lang_code + '-'):
                        return supported_code
        raise LookupError(lang_code)

    def templatize(self, src, origin=None):
        return templatize(src, origin)

    def deactivate_all(self):
        self.deactivate()
        self.deactivate_source()
        self.reset_context()

    def tr(self, label, data=None, description='', options=None):
        return self.context.tr(label, data, description, options)

    def tr_legacy(self, legacy_label, data=None, description='', options=None):
        return self.context.tr_legacy(label, data=data, description=description, options=options)
