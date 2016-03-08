from __future__ import absolute_import
# encoding: UTF-8
from django.utils import translation
from .translator import Translation
from django.conf import settings


__VERSION__ = '0.1.2'


def tr(label, data = None, description = None, options = {}):
    return Translation.instance().context.tr(label, data, description, options)

def activate(locale):
    Translation.instance().activate(locale)

def activate_source(source):
    """ Use source block
        Args:
            source (string): source name
    """
    Translation.instance().activate_source(source)

def deactivate_source():
    Translation.instance().deactivate_source()

def get_languages():
    return Translation.instance().languages

if settings.TML.pop('monkeypatch', False):
    translation._trans = Translation.instance()


