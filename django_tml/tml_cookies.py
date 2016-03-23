import datetime
from django.utils.functional import cached_property
from django.conf import settings
from tml.logger import LoggerMixin
from tml.translator import Translator
from tml.utils import cached_property, cookie_name as get_cookie_name, decode_cookie, encode_cookie


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

    def update(self, response, **kwargs):
        for k, v in kwargs.iteritems():
            self.tml_cookie[k] = v
        self.refresh(response)

    def refresh(self, response):
        self.set_cookie(response, self.cookie_name, encode_cookie(self.tml_cookie))

    def set_cookie(self, response, key, value, days_expire=7):
        if days_expire is None:
            max_age = 365 * 24 * 60 * 60  #one year
        else:
            max_age = days_expire * 24 * 60 * 60
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)
