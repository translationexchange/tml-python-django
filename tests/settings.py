from __future__ import absolute_import, unicode_literals
# -*- encoding: utf-8 -*-
import os
import tempfile
from tml.api.mock import File
from os.path import dirname

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django_tml',
    'tests'
)

DEFAULT_FILE_STORAGE = 'tests.storage.MyFileSystemStorage'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    }
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

MEDIA_ROOT = tempfile.mkdtemp()

SITE_ID = 1
ROOT_URLCONF = 'tests.urls'

SECRET_KEY = 'foobar'

USE_L10N = True

FIXTURES_PATH = dirname(BASE_DIR) + '/tests/fixtures/'

def get_client(key, access_token):
    global FIXTURES_PATH
    return File(FIXTURES_PATH+'/').readdir('')

TML = {
    'api_client': get_client,
    'cache': {'enabled': False},
    'data_preprocessors': ('tml.tools.list.preprocess_lists',),
    'env_generators': ('tml.tools.viewing_user.get_viewing_user',)
}
