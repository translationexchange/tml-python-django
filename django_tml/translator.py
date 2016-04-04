from __future__ import absolute_import
# encoding: UTF-8
import six
from types import FunctionType
from django.conf import settings as django_settings
from django.utils.translation.trans_real import to_locale, templatize, deactivate_all, parse_accept_lang_header, language_code_re, language_code_prefix_re, get_language_from_path
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.module_loading import import_string
from tml import configure, build_context, Key, with_block_options
from tml.application import Application
from tml.session_vars import get_current_context
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
    if 2 == len(exploded):
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
        self._supported_locales = None
        self._client = None
        self.access_token = None
        self.translator = None
        self.init(tml_settings)
        self.context_class = tml_settings.get('context_class', None)
        self.__before_response = set()
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
                             context=self.context_class,
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
        context = get_current_context()
        if context is None:
            context = self.build_context()
        return context

    def context_configured(self):
        return get_current_context() and True or False

    def set_access_token(self, token):
        self.access_token = token
        return self

    def set_translator(self, translator):
        self.translator = translator
        return self

    def get_language(self):
        """ getter to current language """
        locale = self.locale or self.config.default_locale
        return self.config.get(locale, locale)

    def activate(self, locale):
        """ Activate selected language
            Args:
                locale (string): selected locale
        """
        self.locale = locale
        self.reset_context()

    def activate_tml(self, source, access_token=None, translator=None, locale=None):
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
        context = get_current_context()
        if context:
            context.deactivate()

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
        return [str(locale) for locale in self.application.supported_locales]

    def to_locale(self, language):
        return to_locale(language)

    def get_language_from_request(self, request, check_path=False):
        """
        Analyzes the request to find what language the user wants the system to
        show. Only languages listed in settings.LANGUAGES are taken into account.
        If the user requests a sublanguage where we have a main language, we send
        out the main language.
        """
        def get_from_param(request):   # add to flask
            query_param = self.config.locale.get('query_param')
            if request.method.lower() == 'get':
                return request.GET.get(query_param, None)
            else:
                return request.POST.get(query_param, None)

        locale = get_language_from_path(request.path_info) or get_from_param(request)
        cookie_handler = TmlCookieHandler(request, self.application_key)
        if not locale:
            locale = cookie_handler.tml_locale
            # import pdb; pdb.set_trace()
            if not locale:
                if self.config.locale.get('subdomain', None):
                    locale = ".".join(request.META['HTTP_HOST'].split('.')[:-2])
                elif hasattr(request, 'session'):
                    # for backwards compatibility django_language is also checked (remove in 1.8)
                    lang_code = request.session.get(LANGUAGE_SESSION_KEY, request.session.get('django_language'))
                    if lang_code is not None:
                        locale = lang_code
                else:
                    locale = self.get_preferred_languages(request)
        else:
            self.__before_response.add(
                lambda response: cookie_handler.update(response, locale=locale))
        return locale

    def get_preferred_languages(self, request):
        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        for accept_lang, unused in parse_accept_lang_header(accept):
            if accept_lang == '*':
                break
            if not language_code_re.search(accept_lang):
                continue
            if lang_code is not None:
                return accept_lang

    def templatize(self, src, origin=None):
        return templatize(src, origin)

    def deactivate_all(self, response=None):
        while self.__before_response:
            fn = self.__before_response.pop()
            fn(response)
        self.deactivate()
        self.deactivate_source()

    def tr(self, label, data=None, description='', options=None):
        options = options or {}
        return self.context.tr(label, data, description, options)

    def tr_legacy(self, legacy_label, data=None, description='', options=None):
        return self.context.tr_legacy(legacy_label, data=data, description=description, options=options)

    def with_block_options(self, **options):
        if not self.context_configured():
            self.build_context()   # forces context to be configured
        return with_block_options(**options)
