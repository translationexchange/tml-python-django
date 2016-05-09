from __future__ import absolute_import
# encoding: UTF-8
from django.conf import settings
from tml.web_tools.tml_cookies import BaseTmlCookieHandler


class TmlCookieHandler(BaseTmlCookieHandler):

    def get_cookie_from_request(self, request, cookie_name):
        return request.COOKIES.get(cookie_name, None)

    def set_cookie_to_response(self, response, key, value, max_age, expires):
        response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)
