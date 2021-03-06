"""
Django settings for tml demo project.

Generated by 'django-admin startproject' using Django 1.9.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

__autor__ = 'xepa4ep'

import os
pj = os.path.join
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(xnj)ijgghp0rvfl7nguf%c^h*t$e*=o(8z9edyt)mvaqs=*wq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tml',
    'demo'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_tml.middleware.TmlControllerMiddleware'
]

ROOT_URLCONF = 'demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'demo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

def get_gender(x):

    def _get_gender(sex):
        if sex == 1:
            return 'male'
        elif sex == 2:
            return 'female'
        return 'other'

    if hasattr(x, 'items'):
        return _get_gender(x['sex'])
    return _get_gender(getattr(x, 'sex', ''))

TML = {
    'environment': 'dev',
    'application': {'key': '600d6ee64b2c59db3b1244e04ab42c92e50c26459e5e7740ef6a6cc77c76fe34'},
    'monkeypatch': True,
    'cache': {
        'enabled': True,
        'adapter': 'memcached',
        'backend': 'pylibmc',
        'namespace': 'foody'
    },

    # 'context_rules': {
    #     'gender': {
    #         'variables': {
    #             '@gender': lambda x: get_gender(x)
    #         }
    #     }
    # },
    # 'cache': {
    #     'enabled': True,
    #     'adapter': 'file',
    #     'version': 'current',
    #     'path': pj(BASE_DIR, 'tml/cache'),
    #    # 'path': pj(os.path.dirname(BASE_DIR), 'tests/fixtures/snapshot.tar.gz')
    # },
    # 'agent': {
    #     'enabled': True,
    #     'type':    'agent',
    #     'cache':   86400  # timeout every 24 hours
    # },
    #'data_preprocessors': ('tml.tools.list.preprocess_lists',),
    'env_generators': ('tml.tools.viewing_user.get_viewing_user',),
    'logger': {
        'path': pj(BASE_DIR, 'logs', 'tml.log')
    }
}
