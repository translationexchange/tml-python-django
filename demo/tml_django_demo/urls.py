from __future__ import absolute_import
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tml_django_demo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'tml_django_demo.views.home'),
    url(r'^translate$', 'tml_django_demo.views.translate'),
    url(r'^inline_mode', 'tml_django_demo.views.inline_mode'),
    url(r'^auth', 'tml_django_demo.views.auth'),
)
