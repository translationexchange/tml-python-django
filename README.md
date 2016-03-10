<p align="center">
  <img src="https://avatars0.githubusercontent.com/u/1316274?v=3&s=200">
</p>

TML Library for Django
====================================

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

Add tml middleware to MIDDLEWARE_CLASSES setting:

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
        'key': '#',   # add application key from [TranslationExchange dashboard](https://dashboard.translationexchange.com/)
        'path': 'https://staging-api.translationexchange.com',
        'cdn_path': 'http://trex-snapshots.s3-us-west-1.amazonaws.com'},
    'monkeypatch': True,   # support legacy translations
    'cache': {
        'enabled': True,
        'adapter': 'memcached',
        'backend': 'pylibmc',
        'namespace': 'foody'
    },
    'logger': {
        'path': pj(BASE_DIR, 'logs', 'tml.log')
    }
}
```

To start using tml tags and filters, load tag libraries in the head of your template file:

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

For look&feel we will run a demo application that consists of many samples and tml console (iframe app to test your strings).

Instructions:

```
1. Clone the latest code from repository tml-python-django:
git clone git@github.com:translationexchange/tml-python-django.git tml-python-django

2. Navigate to the project demo directory:
cd tml-python-django/demo

3. (optional) Activate environment
virtualenv --no-site-packages tmldemo
. ./tmldemo/bin/activate

4. Install necessary requirements
pip install -r requirements.txt

5. Execute database migration
python manage.py migrate

6. Run your demo
python manage.py runserver

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


