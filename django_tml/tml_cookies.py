from django.utils.functional import cached_property
from tml.logger import LoggerMixin
from tml.translator import Translator
from .utils import cookie_name as get_cookie_name, decode_cookie


class TmlCookieHandler(LoggerMixin):

    def __init__(self, request, application_key):
        self.request = request
        self.cookie_name = get_cookie_name(application_key)

    @cached_property
    def tml_cookie(self):
        cookie = self.request.COOKIES.get(self.cookie_name, None)
        if not cookie:
            cookie = {}
        else:
            try:
                cookie = decode_cookie(cookie)
            except Error as e:
                self.debug("Failed to parse tml cookie: %s", e.message)
                cookie = {}
        return cookie

    @cached_property
    def tml_translator(self):
        translator_data = self.get_cookie('translator')
        return translator_data and Translator(**translator_data) or None

    @cached_property
    def tml_locale(self):
        return self.get_cookie('locale')

    @cached_property
    def tml_access_token(self):
        return self.get_cookie('oauth.token')

    def get_cookie(self, compound_key, default=None):
        key_parts = compound_key.split('.')
        val = self.tml_cookie
        while key_parts and val:
            cur_key = key_parts.pop(0)
            val = val.get(cur_key, default)
        return val or default
