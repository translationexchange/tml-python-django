from __future__ import absolute_import
# encoding: UTF-8
from django.utils.functional import cached_property
from django.conf import settings
from . import activate_source
from .translator import Translation
from tml.translator import Translator
from tml.exceptions import Error
from tml.logger import get_logger

__author__ = 'a@toukmanov.ru, xepa4ep'


class TmlControllerMiddleware(object):
    """ Create source to each view function """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Use source based on view function """
        source = '%s.%s' % (view_func.__module__, view_func.__name__)
        self.translation = Translation.instance()
        self.translation.activate_tml(
            source=source,
            access_token=self.tml_access_token,
            translator=self.tml_translator)
        return None

    def process_response(self, request, response):
        """ Reset source and flush missed keys """
        Translation.instance().deactivate_all()
        return response

    @cached_property
    def tml_cookie(self):
        cookie_name = cookie_name(self.translation.application.key)
        cookie = request.COOKIES.get(cookie_name, None)
        if not cookie:
            cookie = {}
        else:
            try:
                cookie = decode_cookie(cookie, self.translation.application.access_token)
            except Error as e:
                get_logger().debug("Failed to parse tml cookie: %s", e.message)
                cookie = {}
        return cookie

    @cached_property
    def tml_translator(self):
        translator_data = self.get_cookie('translator')
        return translator_data and Translator(self.translation.application, **translator_data) or None

    @cached_property
    def tml_access_token(self):
        return self.get_cookie('oauth.token')

    def get_cookie(self, compound_key, default=None):
        key_parts = compound_key.split('.')
        val = self.cookie
        while key_parts or not val:
            cur_key = key_parts.pop(0)
            val = val.get(cur_key, default)
        return val

