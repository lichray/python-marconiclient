

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
