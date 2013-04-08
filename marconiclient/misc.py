

from urlparse import urlparse, urlunparse
from urllib import quote
from eventlet.green.httplib import HTTPConnection, HTTPSConnection
import json
from exceptions import ClientException
from functools import wraps


def proc_template(template, **kwargs):
    """
    Processes a templated URL by substituting the
    dictionary args and returning the strings.
    """
    res = template

    for name, value in kwargs.iteritems():
        res = res.replace("{" + name + "}", quote(str(value)))

    return res


def require_authenticated(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        token = self._conn._token

        if not token:
            raise ClientException("Authentication Required")

        hdrs = kwargs.get('headers', {})
        hdrs['X-Auth-Token'] = token

        kwargs['headers'] = hdrs

        return f(self, *args, **kwargs)
    return wrapper


def require_clientid(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        client_id = self._conn._client_id

        if not client_id:
            raise ClientException("Client ID Requied")

        hdrs = kwargs.get('headers', {})
        hdrs['Client-Id'] = client_id

        kwargs['headers'] = hdrs

        return f(self, *args, **kwargs)
    return wrapper
