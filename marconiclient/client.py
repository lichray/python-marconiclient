
from eventlet.green.urllib import quote
import eventlet
requests = eventlet.import_patched('requests')

import json
from functools import wraps
from auth import authenticate
from misc import proc_template, require_authenticated
from queue import Queue
from exceptions import ClientException
from urlparse import urljoin

# from eventlet.green.httplib import HTTPConnection, HTTPSConnection

class Connection(object):
    def __init__(self, client_id, auth_endpoint, user, key, **kwargs):
        """
        :param auth_endpoint: The auth URL to authenticate against
        :param user: The user to authenticate as
        :param key: The API key or passowrd to auth with
        """
        self._auth_endpoint = auth_endpoint
        self._user = user
        self._key = key
        self._token = kwargs.get('token')
        self._endpoint = kwargs.get('endpoint')
        self._cacert = kwargs.get('cacert')
        self._client_id = client_id

    @property
    def _conn(self):
        """
        Property to enable decorators to work
        properly
        """
        return self

    @property
    def token(self):
        """The auth token to use"""
        return self._token

    @property
    def auth_endpoint(self):
        """The fully-qualified URI of the auth endpoint"""
        return self._auth_endpoint

    @property
    def endpoint(self):
        """The fully-qualified URI of the endpoint"""
        return self._endpoint

    def connect(self, **kwargs):
        """
        Authenticates the client and returns the endpoint
        """
        headers = {"Client-Id": self._client_id}
        self._session = requests.Session(verify=True, headers=headers)

        if not self._token:
            (self._endpoint, self._token) = authenticate(self._auth_endpoint,
                                                         self._user, self._key,
                                                         endpoint=self._endpoint,
                                                         cacert=self._cacert)
        self._load_homedoc_hrefs()

    def _load_homedoc_hrefs(self):
        """
        Loads the home document hrefs for each endpoint
        Note: at the present time homedocs have not been
        implemented so these hrefs are simply hard-coded. When
        they are implemented we should update this function to
        actually parse the home document.
        """

        # Queues endpoint
        self.queues_href = self._endpoint + "/queues"

        # Specific queue endpoint
        self.queue_href = self.queues_href + "/{queue_name}"

        # Messages endpoint
        self.messages_href = self.queue_href + "/messages"

        # Specific message endpoint
        self.message_href = self.messages_href + "/{message_id}"

        # Claims endpoint
        self._claims_href = self.queues_href + "/claims"

        # Specific claim endpoint
        self._claim_href = self.queues_href + "/claims/{claim_id}"

        # Actions endpoint
        self.actions_href = self._endpoint + "/actions"

        # Specific action endpoint
        self.action_href = self.actions_href + "/{action_id}"

        # Statistics endpoint
        self.stats_href = self.queue_href + "/stats"

    @require_authenticated
    def create_queue(self, queue_name, ttl, headers, **kwargs):
        """
        Creates a queue with the specified name

        :param queue_name: The name of the queue
        :param ttl: The default time-to-live for messages in this queue
        """
        href = proc_template(self.queue_href, queue_name=queue_name)
        body = {u'messages': {u'ttl': ttl}}

        self._perform_http(href=href, method='PUT',
                           request_body=body, headers=headers)

        return Queue(self, href=href, name=queue_name, metadata=body)

    @require_authenticated
    def get_queue(self, queue_name, headers):
        """
        Gets a queue by name

        :param queue_name: The name of the queue
        :param headers: The headers to send to the agent
        """
        href = proc_template(self.queue_href, queue_name=queue_name)

        try:
            hdrs, body = self._perform_http(
                href=href, method='GET', headers=headers)
        except ClientException as ex:
            raise NoSuchQueueError(queue_name) if ex.http_status == 404 else ex

        return Queue(self, href=href, name=queue_name, metadata=body)

    @require_authenticated
    def get_queues(self, headers):
        href = self.queues_href

        hdrs, res = self._perform_http(
            href=href, method='GET', headers=headers)
        queues = res["queues"]

        for queue in queues:
            yield Queue(conn=self._conn, name=queue['name'],
                        href=queue['href'], metadata=queue['metadata'])

    @require_authenticated
    def delete_queue(self, queue_name, headers):
        """
        Deletes a queue

        :param queue_name: The name of the queue
        :param headers: The name
        """
        href = proc_template(self.queue_href, queue_name=queue_name)

        try:
            href = proc_template(self.queue_href, queue_name=queue_name)
            self._perform_http(href=href, method='DELETE', headers=headers)
        except ClientException as ex:
            raise NoSuchQueueError(queue_name) if ex.http_status == 404 else ex

    @require_authenticated
    def get_queue_metadata(self, queue_name, headers, **kwargs):
        href = proc_template(self._queue_href, queue_name=queue_name)
        return self._perform_http(conn, href, 'GET', headers=headers)

    def _perform_http(self, method, headers, href, request_body=''):
        """
        Perform an HTTP operation, checking for appropriate
        errors, etc. and returns the response

        :param conn: The HTTPConnection or HTTPSConnection to use
        :param method: The http method to use (GET, PUT, etc)
        :param body: The optional body to submit
        :param headers: Any additional headers to submit
        :return: (headers, body)
        """
        if not isinstance(request_body, str):
            request_body = json.dumps(request_body)

        url = urljoin(self._endpoint, href)

        response = self._session.request(method=method, url=url,
                                         data=request_body, headers=headers)

        # Check if the status code is 2xx class
        if not response.ok:
            raise ClientException(href=href,
                                  method=method,
                                  http_status=response.status_code,
                                  http_response_content=response.content)

        content_length = int(response.headers.get('Content-Length',0))

        return response.headers, response.json if content_length else ''
