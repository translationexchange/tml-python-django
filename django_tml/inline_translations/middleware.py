from __future__ import absolute_import
# encoding: UTF-8
from .. import inline_translations as _
from django.conf import settings

class InlineTranslationsMiddleware(object):
    """ Turn off/on inline tranlations with cookie """
    def process_request(self, request, *args, **kwargs):
        """ Check signed cookie for inline tranlations """
        try:
            if request.get_signed_cookie(self.cookie_name):
                # inline tranlation turned on in cookies:
                _.turn_on()
                return None
        except KeyError:
            # cookie is not set
            pass
        else:
            # Turn off by default:
            _.turn_off()
        return None

    @property
    def cookie_name(self):
        return settings.TML.get('inline_translation_cookie', 'inline_translations')

    def process_response(self, request, response):
        """ Set/reset cookie for inline tranlations """
        if _.save:
            if _.enabled:
                response.set_signed_cookie(self.cookie_name, True)
            else:
                response.delete_cookie(self.cookie_name)
            _.save = False # reset save flag
        _.turn_off() # turn off tranlation after request executed
        return response

