<p align="center">
  <img src="https://avatars0.githubusercontent.com/u/1316274?v=3&s=200">
</p>

TML Library for Django
====================================
[![Build Status](https://travis-ci.org/translationexchange/tml-python-django.png?branch=master)](https://travis-ci.org/translationexchange/tml-python-django)
[![Coverage Status](https://coveralls.io/repos/translationexchange/tml-python-django/badge.png?branch=master)](https://coveralls.io/r/translationexchange/tml-python-django?branch=master)


## Introduction

This document demonstrates how to use TML (Translation Markup Language) in a Django application.

### Integration

Installing using pip:

```
pip install django_tml
```

Add 'django_tml' to your INSTALLED_APPS setting:

```python
INSTALLED_APPS = (
    ...
    'django_tml',
)
```

Add TML middleware to MIDDLEWARE_CLASSES setting:

```
MIDDLEWARE_CLASSES = (
  ...
  'django_tml.middleware.TmlControllerMiddleware',
)
```

Then add the following TML configuraiton to setting file:

```python
TML = {
    'environment': 'dev',
    'application': {
        'key': 'YOUR_APPLICATON_KEY',   # add application key from [TranslationExchange dashboard](https://dashboard.translationexchange.com/)
    },
    'monkeypatch': True,   # support legacy translations
    'cache': {
        'enabled': True,
        'adapter': 'memcached',
        'host': '127.0.0.1:11211',
        'backend': 'pylibmc',
        'namespace': 'foody'
    },
    'logger': {
        'path': pj(BASE_DIR, 'logs', 'tml.log')
    }
}
```

To start using TML tags and filters, load tag libraries in the head of your template file:

```jinja2
{­% load i18n %­}
{­% load tml tml_inline %­}
```

To activate inline translation functionality add one more line in the head section of your layout:

```jinja2
{­% tml_inline_header %­}
```

*(Optional)* You can also add a language switcher to your site. Just add the next template tag in the navigation of your site:

```jinja2
{% tml_language_selector type="sideflags" %}
```

### Demo application

The best way to learn about the SDK capabilities is to use the demo application that comes with the SDK. The demo application provides many samples of TML syntax.

Run the following scripts to setup and run the the Demo application: 

```bash
$ git clone git@github.com:translationexchange/tml-python-django.git
$ cd tml-python-django/demo
$ virtualenv --no-site-packages tmldemo
$ . ./tmldemo/bin/activate
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py runserver localhost:8000
```

### TML Configuration

* ``environment`` - Running environment (one of ``dev|stage|prod``)
* ``application`` - Provide key for authentication, api path and cdn path to and path api path.
* ``monkeypatch`` - This option facilitates Tml to be backward compatible with django i18n engine. You can still use django native tags for translating your strings.
* ``cache`` - Define your cache configuration here. More about cache in advanced section.
* ``agent`` - Agent helps your application to download JS SDK on initial load of your page and then use TML widgets, shortcuts and SDK in client-side.
* ``data_preprocessors`` - Preprocessors applied on translateable string before actual processing. For example ``list`` preprocessors preprocess list like context variable into meaningful text token.
* ``env_generators`` - Sometimes you do not need to provide substitution token variable. For example, ``viewing_user`` env generator could be substituted by the return value of env generator. By default we return ``request.user``.
* ``logger`` - TML log that tracks interaction with SDK by http and supressed exceptions while translating string.


Links
==================

* Register on TranslationExchange.com: http://translationexchange.com

* Follow TranslationExchange on Twitter: https://twitter.com/translationx

* Connect with TranslationExchange on Facebook: https://www.facebook.com/translationexchange

* If you have any questions or suggestions, contact us: support@translationexchange.com


Copyright and license
==================

Copyright (c) 2016 Translation Exchange, Inc.

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

