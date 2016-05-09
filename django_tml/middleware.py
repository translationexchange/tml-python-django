from __future__ import absolute_import
# encoding: UTF-8
import re
from django.utils.functional import cached_property
from django.conf import settings
from django.template import Template
from django.template.context import Context
from tml.exceptions import Error
from .translator import Translation
from .tml_cookies import TmlCookieHandler

__author__ = 'a@toukmanov.ru, xepa4ep'


_HTML_TYPES = ('text/html', 'application/xhtml+xml')


class TmlControllerMiddleware(object):
    """ Create source to each view function """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Use source based on view function """
        source = '%s.%s' % (view_func.__module__, view_func.__name__)
        self.translation = Translation.instance()
        cookie_handler = TmlCookieHandler(request, self.translation.application_key)
        locale = self.translation.get_language_from_request(request, True)
        self.translation.activate_tml(
            source=source,
            access_token=cookie_handler.tml_access_token,
            translator=cookie_handler.tml_translator,
            locale=locale)
        request.TML = self.translation.config
        return None

    def process_response(self, request, response):
        """Teardown tml"""
        if not self.translation:
            return response
        if self.translation.config['agent']['enabled'] and self.translation.config['agent']['force_injection']:
            if not getattr(response, 'streaming', False):
                is_gzipped = 'gzip' in response.get('Content-Encoding', '')
                is_html = response.get('Content-Type', '').split(';')[0] in _HTML_TYPES
                if is_html and not is_gzipped:
                    pattern = re.compile(b'</head>', re.IGNORECASE)
                    agent_script = Template('{% load tml_inline %}{% tml_inline_header %}').render(Context({'request': request, 'caller': 'middleware'}))
                    # import pdb; pdb.set_trace()
                    response.content = pattern.sub(bytes(agent_script) + b'</head>', response.content)
                    response['Content-Length'] = len(response.content)

        # teardown
        self.translation.deactivate_all(response)
        self.request = None
        self.translation = None
        return response

