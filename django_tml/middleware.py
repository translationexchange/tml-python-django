from __future__ import absolute_import
# encoding: UTF-8
from django.utils.functional import cached_property
from django.conf import settings
from tml.exceptions import Error
from .translator import Translation
from .tml_cookies import TmlCookieHandler

__author__ = 'a@toukmanov.ru, xepa4ep'


class TmlControllerMiddleware(object):
    """ Create source to each view function """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Use source based on view function """
        source = '%s.%s' % (view_func.__module__, view_func.__name__)
        self.translation = Translation.instance()
        locale = self.translation.get_language_from_request(request, True)
        cookie_handler = TmlCookieHandler(request, self.translation.application_key)
        self.translation.activate_tml(
            source=source,
            access_token=cookie_handler.tml_access_token,
            translator=cookie_handler.tml_translator,
            locale=locale)
        return None

    def process_response(self, request, response):
        """ Reset source and flush missed keys """
        Translation.instance().deactivate_all()
        self.request = None
        self.translation = None
        return response

