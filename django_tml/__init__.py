from __future__ import absolute_import
# encoding: UTF-8
from django.utils import translation
from .translator import Translation
from django.conf import settings
from tml.logger import get_logger
from tml import get_context as get_current_context, get_current_language, get_current_locale, with_block_options


__VERSION__ = '0.1.8'


def tr(label, data = None, description = None, options = {}):
    _, value, error = Translation.instance().tr(label, data, description, options)
    if error:
        get_logger().exception(error)
    return value

def gettext(label):
    return ugettext(label)

def ugettext(label):
    return Translation.instance().ugettext(label)

def ungettext(singular, plural, number):
    return Translation.instance().ungettext(label)

def pgettext(context, label):
    return Translation.instance().pgettext(context, label)

def npgettext(context, singular, plural, number):
    return Translation.instance().npgettext(context, singular, plural, number)

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


