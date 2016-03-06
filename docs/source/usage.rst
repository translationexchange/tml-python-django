========
Usage
========

In order to start using Django TML you should already install and configure TML. It was described clearly in previous sections.


Configuration
-------------

.. note:: Putting your private keys in codebase is bad practice. Keep them outside of your project folder.

Here is minimal configuration::

    import os
    ...

    TML = {
      'environment': 'dev',
      'application': {'key': '#'},
      'monkeypatch': True,
      'cache': {
          'enabled': True,
          'adapter': 'memcached',
          'backend': 'pylibmc',
          'namespace': 'foody'
      },
      # 'cache': {
      #     'enabled': True,
      #     'adapter': 'file',
      #     'version': '20160303075532',
      #     'path': os.path.join(BASE_DIR, 'tml/cache')
      #    # 'path': os.path.join(os.path.dirname(BASE_DIR), 'tests/fixtures/snapshot.tar.gz')
      # },
      'agent': {
          'enabled': True,
          'type':    'agent',
          'cache':   86400  # timeout every 24 hours
      },
      'data_preprocessors': ('tml.tools.list.preprocess_lists',),
      'env_generators': ('tml.tools.viewing_user.get_viewing_user',),
      'logger': {
          'path': os.path.join(BASE_DIR, 'logs', 'tml.log')
      }
  }



Explanation:

 * ``environment`` - Running environment (one of ``dev|stage|prod``)
 * ``application`` - Provide key and secret (optional) of your app from `translation exchange <http://translationexchange.com>` e.g. ``{key: '', token: ''}``.
 * ``monkeypatch`` - This option facilitates Tml to be backward compatible with django i18n engine. You can still use django native tags for translating your strings.
 * ``cache`` - Define your cache configuration here. More about cache in advanced section.
 * ``agent`` - Agent helps your application to download JS SDK on initial load of your page and then use TML widgets, shortcuts and SDK in client-side.
 * ``data_preprocessors`` - Preprocessors applied on translateable string before actual processing. For example ``list`` preprocessors preprocess list like context variable into meaningful text token.
 * ``env_generators`` - Sometime you do not need to provide substitution token variable. For example, ``viewing_user`` env generator could be substituted by the return value of env generator. By default we return ``request.user``.
 * ``logger`` - TML log.


.. note:: ``env_generators`` and ``data_preprocessors`` are configured by default.


Simple Translations
-------------------

Translations with Dynamic Context
----------------------------------------

Virtual sources
---------------


Dummy application
-----------------
