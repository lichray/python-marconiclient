from misc import http_connect, proc_template, perform_http, require_authenticated
from misc import require_clientid, replace_endpoint

from message import Message

class NoSuchQueueError(Exception):
    def __init__(self, name):
        pass

class Queue(object):

    def __init__(self, conn, name, endpoint):
        """
        Creates a new queue object. This class should
        never be instantiated directly but should be
        used with Connection.create_queue or
        Connection.get_queue
        """
        self._conn = conn
        self._endpoint = endpoint
        self._name = name


    @require_authenticated
    @require_clientid
    def post_message(self, message, ttl, headers, **kwargs):
        """
        Posts a single message with the specified ttl
        :param ttl: The TTL to set on this message
        """
        url = proc_template(self._conn.messages_url, queue_name=self.name)

        body = [{"ttl": ttl, "body": message}]

        hdrs, body = perform_http(url=url, method='POST', body=body, headers=headers)

        location = hdrs['location']
        location = replace_endpoint(url, location)

        return Message(conn=self._conn, url=location)

    @property
    def name(self):
        """The name of this queue"""
        return self._name
