from __future__ import absolute_import, unicode_literals
import os
import pytest
from copy import deepcopy
from django import conf

# encoding: UTF-8
__author__ = 'a@toukmanov.ru, xepa4ep'

def pytest_configure():
    os.environ[conf.ENVIRONMENT_VARIABLE] = "tests.settings"

    try:
        import django
        django.setup()
    except AttributeError:
        pass

    from django.test.utils import setup_test_environment

    setup_test_environment()

    from django.db import connection

    connection.creation.create_test_db()


def unittest_fixture(request, key, value):
    setattr(request.cls, key, value)


@pytest.fixture(scope="class")
def activate(request):
    from tml.context import LanguageContext
    from django_tml.translator import Translation

    def _activate(self, locale, tml_settings=None, skip=False):
        tml_settings = deepcopy(tml_settings or {})
        if not skip:
            tml_settings['context_class'] = LanguageContext
        t = Translation.instance(tml_settings=tml_settings)
        t.activate(locale)
        return t
    return unittest_fixture(request, 'activate', _activate)
