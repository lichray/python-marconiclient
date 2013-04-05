

from urlparse import urlparse, urlunparse
from urllib import quote
from eventlet.green.httplib import HTTPConnection, HTTPSConnection
import json
from exceptions import ClientException
from functools import wraps

def http_connect(url):
    """Creates an HTTP/HTTPSConnection object, as appropriate and
    returns a tuple containing the parsed URL and connection

    :param url: The url that's going to be used with this connection"""

    parsed = urlparse(url)

    if parsed.scheme == 'http':
        conn = HTTPConnection(parsed.netloc)
    elif parsed.scheme == 'https':
        conn = HTTPSConnection(parsed.netloc)
    else:
        raise ClientException('Cannot handle protocol %s for url %s' %
                              (parsed.scheme, repr(url)))

    return parsed, conn


def perform_http(method, headers, url, body=''):
    """
    Perform an HTTP operation, checking for appropriate
    errors, etc. and returns the response

    :param conn: The HTTPConnection or HTTPSConnection to use
    :param method: The http method to use (GET, PUT, etc)
    :param body: The optional body to submit
    :param headers: Any additional headers to submit
    :return: (headers, body)
    """
    parsed, conn = http_connect(url)

    # If the user passed in a dict, list, etc. serialize to JSON
    if not isinstance(body, str):
        body = json.dumps(body)

    conn.request(method, parsed.path, body, headers=headers)

    response = conn.getresponse()

    # Check if the status code is 2xx class
    if response.status // 100 != 2:
        raise ClientException(url=url,
                              method=method,
                              http_status=response.status,
                              http_response_content=response.read())

    headers = response.getheaders()
    body = response.read()

    if len(body) > 0:
        body = json.loads(body, encoding='utf-8')

    conn.close()

    return dict(headers), body


def proc_template(template, **kwargs):
    """
    Processes a templated URL by substituting the
    dictionary args and returning the strings.
    """
    res = template

    for name, value in kwargs.iteritems():
        res = res.replace("{"+name+"}", quote(str(value)))

    return res


def require_authenticated(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        token = self._conn._token

        if not token:
            raise ClientException("Authentication Required")

        hdrs = kwargs.get('headers',{})
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

        hdrs = kwargs.get('headers',{})
        hdrs['Client-Id'] = client_id

        kwargs['headers'] = hdrs

        return f(self, *args, **kwargs)
    return wrapper

def replace_endpoint(url, endpoint):
    """
    Given a URL, replace the endpoint with the
    specified endpoint
    """
    parsed = urlparse(url)
    parts = list(parsed)
    parts[2] = endpoint
    parts[3] = ""
    parts[4] = ""
    return urlunparse(parts)
