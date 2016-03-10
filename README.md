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
        'key': '6c377447a542718bfd9fe0f5d8f11fae2827377bc4295db76667469db67bd8ed',
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

*(Optional)* You can also add a language switcher in the navigation of your layout:

```jinja2
{% tml_language_selector type="sideflags" %}
```
