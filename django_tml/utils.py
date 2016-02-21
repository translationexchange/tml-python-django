from __future__ import absolute_import
# encoding: UTF-8
import json
import base64
from datetime import datetime, timedelta
from time import mktime
from tml.tools.viewing_user import reset_viewing_user, set_viewing_user
from tml.rules.contexts.gender import Gender
from .exceptions import CookieParseError

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
    try:
        data = json.loads(base64.b64decode(base64_payload))
        # TODO: Verify signature
        return data
    except Exception as e:
        raise CookieParseError(e)
