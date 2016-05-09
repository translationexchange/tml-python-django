from __future__ import absolute_import
# encoding: UTF-8
from django.conf import settings as django_settings
from django.utils.translation.trans_real import to_locale, templatize, deactivate_all, parse_accept_lang_header, language_code_re, language_code_prefix_re, get_language_from_path, to_locale
from django.utils.translation import LANGUAGE_SESSION_KEY
from tml.web_tools.translator import BaseTranslation
from .tml_cookies import TmlCookieHandler


author = 'a@toukmanov.ru, xepa4ep'


class Translation(BaseTranslation):
    """ Basic translation class """

    @classmethod
    def instance(cls, tml_settings=None):
        """ Singletone
            Returns:
                Translation
        """
        if cls._instance is None:
            cls._instance = cls(tml_settings or getattr(django_settings, 'TML', {}))
        return cls._instance

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
            self._before_response.add(
                lambda response: cookie_handler.update(response, locale=locale))
        return locale

    def get_header_from_request(self, request, header):
        return request.META.get('HTTP_ACCEPT_LANGUAGE', '')

    def templatize(self, src, origin=None):
        return templatize(src, origin)

    def deactivate_all(self, response=None):
        while self._before_response:
            fn = self._before_response.pop()
            fn(response)
        self.deactivate()
        self.deactivate_source()

    def to_locale(self, language):
        return to_locale(language)
