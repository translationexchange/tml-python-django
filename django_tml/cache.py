from __future__ import absolute_import
# encoding: UTF-8
from django.conf import settings
from django.core.cache import caches
from tml.api.client import Client
try:
    from urllib import urlencode
except ImportError:
    # PY3
    from urllib.parse import urlencode

class CachedClient(object):
    def __init__(self, client, backend):
        self.client = client
        self.backend = backend

    @classmethod
    def instance(cls):
        client = Client(settings.TML.get('token'))
        return cls.wrap(client)

    @classmethod
    def wrap(cls, client):
        backend_name = settings.TML.get('cache', None)
        if backend_name is None:
            return client
        return cls(client, caches[backend_name])

    def key(self, url, params):
        return '%s?%s' % (url, urlencode(params))

    def get(self, url, params = {}):
        """ GET request to API 
            Args:
                url (string): URL
                params (dict): params
            Raises:
                APIError: API returns error
            Returns:
                dict: response
        """
        key = self.key(url, params)
        ret = self.backend.get(key)
        if not ret is None:
            return ret
        ret = self.client.get(url, params)
        self.backend.set(key, ret)
        return ret

    def post(self, url, params):
        return self.client.post(url, params)

    def reload(self, url, params):
        """ Drop cache """
        self.backend.delete(self.key(url, params))
