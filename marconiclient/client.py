from urllib import quote

import json
from functools import wraps
from auth import authenticate
from misc import http_connect, proc_template, perform_http, require_authenticated
from queue import Queue
from exceptions import ClientException


class Connection(object):
    def __init__(self, client_id, auth_url, user, key, **kwargs):
        """
        :param auth_url: The auth URL to authenticate against
        :param user: The user to authenticate as
        :param key: The API key or passowrd to auth with
        """
        self._auth_url = auth_url
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
    def auth_url(self):
        """The fully-qualified URI of the auth endpoint"""
        return self._auth_url


    @property
    def endpoint(self):
        """The fully-qualified URI of the endpoint"""
        return self._endpoint


    def connect(self, **kwargs):
        """
        Authenticates the client and returns the endpoint
        """
        if not self._token:
            (self._endpoint, self._token) = authenticate(self._auth_url,
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
        self.queues_url = self._endpoint + "/queues"

        # Specific queue endpoint
        self.queue_url = self.queues_url + "/{queue_name}"

        # Messages endpoint
        self.messages_url = self.queue_url + "/messages"

        # Specific message endpoint
        self.message_url = self.messages_url + "/{message_id}"

        # Actions endpoint
        self.actions_url = self._endpoint + "/actions"

        # Specific action endpoint
        self.action_url = self.actions_url + "/{action_id}"


    @require_authenticated
    def create_queue(self, queue_name, ttl, headers, **kwargs):
        """
        Creates a queue with the specified name

        :param queue_name: The name of the queue
        :param ttl: The default time-to-live for messages in this queue
        """
        url = proc_template(self.queue_url, queue_name=queue_name)
        body = {"messages": {"ttl": ttl}}

        perform_http(url=url, method='PUT',
                          body=body, headers=headers)

        return Queue(self, endpoint=url, name=queue_name)


    @require_authenticated
    def get_queue(self, queue_name, headers):
        """
        Gets a queue by name

        :param queue_name: The name of the queue
        :param headers: The headers to send to the agent
        """

        url = proc_template(self.queue_url, queue_name=queue_name)

        try:
            hdrs, body = perform_http('GET', url)
        except ClientException as ex:
            raise NoSuchQueueError(queue_name) if ex.http_status == 404 else ex

        return Queue(self, endpoint=url, name=queue_name)


    @require_authenticated
    def delete_queue(self, queue_name, headers):
        """
        Deletes a queue

        :param queue_name: The name of the queue
        :param headers: The name
        """
        url = proc_template(self.queue_url, queue_name=queue_name)

        try:
            url = proc_template(self.queue_url, queue_name=queue_name)
            perform_http(url=url, method='DELETE', headers=headers)
        except ClientException as ex:
            raise NoSuchQueueError(queue_name) if ex.http_status == 404 else ex


    @require_authenticated
    def get_queue_metadata(self, queue_name, headers, **kwargs):
        url = proc_template(self._queue_url, queue_name=queue_name)
        return perform_http(conn, url, 'GET', headers=headers)
