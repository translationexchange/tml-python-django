from __future__ import absolute_import
# encoding: UTF-8
from django.contrib.auth.models import User
from django_tml.utils import ViewingUserMiddleware

from tml import Gender
from hashlib import md5
import six

GENDERS = {}

class LoginBackend(object):
    def authenticate(self, name, gender = None):
        gender = Gender.supported_gender(gender)

        username = six.u('%s:%s') % (gender, name)
        username = md5(username.encode('utf-8')).hexdigest()
        try:
            return User.objects.get(username = username)
        except Exception:
            user = User()
            user.username = username
            user.first_name = name
            user.last_name = gender
            user.save()
            return user

    def get_user(self, id):
        return User.objects.get(id = id)

class DemoViewingUserMiddleware(ViewingUserMiddleware):
    def build_gender(self, user):
        return Gender(user.last_name, user.first_name)