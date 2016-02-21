from __future__ import absolute_import
# encoding: UTF-8
from .. import Translation
import six
enabled = False
save = False

def turn_on():
    """ Turn on inline tranlations """
    global enabled
    Translation.instance().turn_off_cache()
    enabled = True

def turn_off():
    """ Turn off inline translations """
    global enabled
    Translation.instance().turn_on_cache()
    enabled = False


def turn_on_for_session():
    """ Turn on and remember in cookies """
    global save
    turn_on()
    save = True

def turn_off_for_session():
    """ Turn off and remember in cookies """
    global save
    turn_off()
    save = True

def wrap_string(text, key, translated):
    """ Wrap string with tranlation """
    global enabled
    if not enabled:
        return text
    class_name = 'tml_translated' if translated else 'tml_not_translated'
    return six.u('<tml:label class="tml_translatable %(class_name)s" data-translation_key="%(key)s" data-target_locale="%(locale)s">%(text)s</tml:label>') % ({'key':key.key, 'text':text, 'class_name': class_name, 'locale': Translation.instance().context.locale})

