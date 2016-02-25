from __future__ import absolute_import
# encoding: UTF-8
import json
from datetime import datetime, timedelta
from time import mktime
from tml.tools.viewing_user import reset_viewing_user, set_viewing_user
from tml.rules.contexts.gender import Gender
from urllib import unquote
from .exceptions import CookieNotParsed

__author__ = 'a@toukmanov.ru, xepa4ep'


class ViewingUserMiddleware(object):
    """ Middleware for viewing user """
    def process_request(self, request):
        if request.user.is_authenticated():
            set_viewing_user(self.build_gender(request.user))
        else:
            reset_viewing_user()
        return None

    def build_gender(self, user):
        return Gender.other(user.firstname)

    def process_response(self, request, response):
        """ Reset source and flush missed keys """
        reset_viewing_user()
        return response


def ts():
    return int(mktime(datetime.utcnow().timetuple()))


def cookie_name(app_key):
    return 'trex_%s' % app_key


def decode_cookie(base64_payload, secret=None):
    padding_chars = '==='
    try:
        data = json.loads((unquote(base64_payload)).decode('base64', 'strict'))
        # TODO: Verify signature
        return data
    except Exception as e:
        raise CookieNotParsed(e)
