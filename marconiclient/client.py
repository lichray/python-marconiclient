
from urllib import quote
from urlparse import urlparse

import json

from eventlet.green.httplib import HTTPConnection, HTTPSConnection


class ClientException(Exception):
    """Exception for wrapping up maconi client errors
    """
    def __init__(self, msg, http_scheme='', http_host='',
                 http_port='', http_path='', http_query='', http_status=0,
                 http_reason='', http_device='', http_response_content=''):
        Exception.__init__(self, msg)

        self.msg = msg
        self.http_scheme = http_scheme
        self.http_host = http_host
        self.http_port = http_port
        self.http_path = http_path
        self.http_query = http_query
        self.http_status = http_status
        self.http_reason = http_reason
        self.http_device = http_device
        self.http_response_content = http_response_content


# This code shamelessly borrowed from python-swiftclient
def authenticate(auth_url, user, key, os_options, **kwargs):
    insecure = kwargs.get('insecure', False)

    from keystoneclient.v2_0 import client as ksclient
    from keystoneclient import exceptions

    try:
        _ksclient = ksclient.Client(username=user,
                                    password=key,
                                    tenant_name=os_options.get('tenant_name'),
                                    tenant_id=os_options.get('tenant_id'),
                                    cacert=kwargs.get('cacert'),
                                    auth_url=auth_url, insecure=insecure)

    except exceptions.Unauthorized:
        raise ClientException('Unauthorized. Check username, password'
                              ' and tenant name/id')

    except exceptions.AuthorizationFailure, err:
        raise ClientException('Authorization Failure. %s' % err)

    # TODO(jdp): Ensure that this is the correct service_type field
    service_type = os_options.get('service_type') or 'queueing'
    endpoint_type = os_options.get('endpoint_type') or 'publicURL'

    try:
        endpoint = _ksclient.service_catalog.url_for(
            attr='region',
            filter_value=os_options.get('region_name'),
            service_type=service_type,
            endpoint_type=endpoint_type)
    except exceptions.EndpointNotFound:
        # Since no endpoint was found, we let it default to None
        # so that we can remove them
        endpoint = None

    return (endpoint, _ksclient.auth_token)


class Connection(object):

    def __init__(self, authurl, user, key, region=None, endpoint=None):
        """
        :param authurl: The auth URL to authenticate against
        :param user: The user to authenticate as
        :param key: The API key or passowrd to auth with
        """
        self._authurl = authurl
        self._user = user
        self._key = key
        self._token = None

        self._endpoint = endpoint

    @property
    def token(self):
        return self._token

    @property
    def authurl(self):
        return self._authurl

    @property
    def endpoint(self):
        return self._endpoint

    def connect(self, **kwargs):
        """Authenticates (if necessary) the client"""

        auth_version = kwargs.get('auth_version', '2.0')
        os_options = kwargs.get('os_options', {})

        if auth_version in ['2.0', '2', 2]:
            insecure = kwargs.get('insecure', False)
            cacert = kwargs.get('cacert', None)

            (endpoint, self._token) = authenticate(self._authurl,
                                                   self._user, self._key,
                                                   os_options, cacert=cacert,
                                                   insecure=insecure)

            if not self._endpoint:
                self._endpoint = endpoint

            if not self._endpoint:
                raise ClientException("No Marconi endpoint specified " +
                                      "and no endpoint found.")

            return

        raise ClientException(
            'Unknown auth_version %s specified.' % auth_version)

    def http_connection(self, url, proxy=None):
        """Makes an HTTP/HTTPSConnection as appropriate

        :param url: url to connect to
        :raises ClientException: Unable to handle protocol scheme
        """
        # TODO?
        # url = encode_utf8(url)
        parsed = urlparse(url)
        proxy_parsed = urlparse(proxy) if proxy else None
        if parsed.scheme == 'http':
            conn = HTTPConnection((proxy_parsed if proxy else parsed).netloc)
        elif parsed.scheme == 'https':
            conn = HTTPSConnection((proxy_parsed if proxy else parsed).netloc)
        else:
            raise ClientException('Cannot handle protocol %s for url %s' %
                                  (parsed.scheme, repr(url)))

        return parsed, conn

    def create_queue(self, queuename, ttl):
        """Creates a queue with the specified name

        :param queuename: The name of the queue
        :param ttl: The default time-to-live for messages in this queue
        """
        parsed, conn = self.http_connection(url=self._endpoint)

        method = 'PUT'
        path = '%s/queues/%s' % (parsed.path, quote(queuename))

        headers = {'X-Auth-Token': self._token}

        body_raw = {"messages": {"ttl": ttl}}

        conn.request(method, path, json.dumps(body_raw), headers)

        resp = conn.getresponse()

        if resp.status not in [200, 201]:
            raise ClientException("Error creating queue")

    def get_queue_metadata(self, queuename, **kwargs):
        """

        :param queuename: The name of the queue to use
        """
        parsed, conn = self.http_connection(url=self._endpoint)

        method = 'GET'
        path = '%s/queues/%s' % (parsed.path, quote(queuename))

        headers = {'X-Auth-Token': self._token}

        conn.request(method, path, '', headers)

        resp = conn.getresponse()

        if resp.status == 404:
            raise ClientException("No such queue: %s" % (queuename))

        if resp.status != 200:
            raise ClientException(
                "Error fetching metadata for queue %s" % (queuename), resp)

        body = resp.read()

        return json.loads(body)
