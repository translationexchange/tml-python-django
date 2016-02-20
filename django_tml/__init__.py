from __future__ import absolute_import
# encoding: UTF-8
from django.utils import translation
from .translator import Translator
from django.conf import settings

def tr(label, data = None, description = None, options = {}):
    return Translator.instance().context.tr(label, data, description, options)

def activate(locale):
    Translator.instance().activate(locale)

def activate_source(source):
    """ Use source block
        Args:
            source (string): source name
    """
    Translator.instance().activate_source(source)

def deactivate_source():
    Translator.instance().deactivate_source()

def enter_source(source):
    """ Enter source block
        Args:
            source (string): source name
    """
    Translator.instance().enter_source(source)

def exit_source():
    """ Exit from source block
        Args:
            source (string): source name
    """
    Translator.instance().exit_source()

def get_languages():
    return Translator.instance().languages

if settings.TML.get('monkeypatch', False):
    translation._trans = Translator.instance()


