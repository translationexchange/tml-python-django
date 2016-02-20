from __future__ import absolute_import
# encoding: UTF-8
from tml.tools.viewing_user import reset_viewing_user, set_viewing_user
from tml.rules.contexts.gender import Gender

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