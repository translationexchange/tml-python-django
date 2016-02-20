from __future__ import absolute_import
# encoding: UTF-8
from . import activate_source
from .translator import Translator
from django.conf import settings

class SetSourceToViewMiddleware(object):
    """ Create source to each view function """
    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Use source based on view function """
        Translator.instance().activate_source('%s.%s' % (view_func.__module__, view_func.__name__))
        return None

    def process_response(self, request, response):
        """ Reset source and flush missed keys """
        Translator.instance().deactivate_all()
        return response

