from __future__ import absolute_import
# encoding: UTF-8
from django.utils import translation
from .translator import Translation
from django.conf import settings
from tml.logger import get_logger


__VERSION__ = '0.1.6'


def tr(label, data = None, description = None, options = {}):
    _, value, error = Translation.instance().context.tr(label, data, description, options)
    if error:
        get_logger().exception(error)
    return value

def activate(locale, dry_run=False, tml_settings=None):
    Translation.instance(tml_settings=tml_settings).activate(locale, dry_run=dry_run)

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


