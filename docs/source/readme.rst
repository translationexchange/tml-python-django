=============================
django-tml
=============================

Documentation
-------------

This Client SDK provides tools for translating Django applications into any language using the TranslationExchange.com service.

Dependencies
------------

Support python versions: 2.7, 3.3, 3.4, 3.5.

Services: memcached

The list of dependencies::

    tml>=0.2.6
    django>=1.7


Quickstart
----------

Install using pip::

    pip install django_tml

Add ``django_tml`` to ``INSTALLED_APPS`` and ``django_tml.middleware.TmlControllerMiddleware`` to your ``MIDDLEWARE_CLASSES``. Do not forget to configure the ``TML`` setting. Here is the minimal configuration to start using TML with cache::

    import os
    ...

    TML = {
        'environment': 'dev',
        'application': {'key': '#key'},
        'monkeypatch': True,   # support django native translation utilities
        'cache': {
             'enabled': True,
             'adapter': 'file',
             'version': '...',
        },
        'logger': {
            'path': os.path.join(BASE_DIR, 'logs', 'tml.log')
        }
    }

Start using TML in your templates::

    {% load tml tml_inline %}   # TML template tags and filters
    {% load i18n %}   # django native template tags and filters

In the head section of your layout add::

    {­% tml_inline_header %­}

Tml is configured. Now you can translate your first string::

    <title>{% trs "TML is awesome" %}</title>

You can add language switcher into your navigation layout to test translations across languages:

    {% tml_language_selector type="sideflags" %}


Credits
---------


