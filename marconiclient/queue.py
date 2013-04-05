from misc import http_connect, proc_template, perform_http, require_authenticated
from misc import require_clientid, replace_endpoint

from message import Message

class NoSuchQueueError(Exception):
    def __init__(self, name):
        pass

class Queue(object):

    def __init__(self, conn, name, endpoint, metadata=None):
        """
        Creates a new queue object. This class should
        never be instantiated directly but should be
        used with Connection.create_queue or
        Connection.get_queue
        """
        self._conn = conn
        self._endpoint = endpoint
        self._name = name
        self._metadata = metadata

        self._messages_template = endpoint + "/messages"
        self._message_template = endpoint + "/messages/{message_id}"
        self._claims_template = endpoint + "/claims?limit={limit}"
        self._claim_template = endpoint + "/claims/{claim_id}"

    @property
    def metadata(self):
        return self._metadata


    @require_authenticated
    @require_clientid
    def set_metadata(self, metadata, headers, **kwargs):
        perform_http(url=self._endpoint, method='PUT', request_body=metadata, headers=headers)
        self._metadata = metadata


    @require_authenticated
    @require_clientid
    def post_message(self, message, ttl, headers, **kwargs):
        """
        Posts a single message with the specified ttl
        :param ttl: The TTL to set on this message
        """
        url = proc_template(self._conn.messages_url, queue_name=self.name)

        body = [{"ttl": ttl, "body": message}]

        hdrs, body = perform_http(url=url, method='POST', request_body=body, headers=headers)

        location = hdrs['location']
        location = replace_endpoint(url, location)

        return Message(conn=self._conn, url=location)


    @require_authenticated
    @require_clientid
    def claim_messages(self, headers, ttl, grace, limit=5, **kwargs):
        """
        Claims a set of messages. The server configuration determines
        the maximum number of messages that can be claimed.
        """
        url = proc_template(self._claims_template, limit=limit)


        body = {"ttl":ttl, "grace":grace}

        hdrs, body = perform_http(url=url, method='POST', request_body=body, headers=headers)

        for msg in body:
            msgurl = replace_endpoint(url, msg['href'])
            yield Message(self._conn, url=msgurl, content=msg)


    @require_authenticated
    @require_clientid
    def get_messages(self, headers, **kwargs):

        """
        TODO(jdp): Support pagination

        Lists all messages in this queue:w
        """
        url = proc_template(self._conn.messages_url, queue_name=self.name)

        truncated=True# Was the current request truncated?

        while truncated:
            truncated = False

            hdrs, body = perform_http(url=url, method='GET', headers=headers)

            if not body:
                # Empty body, just short-circuit and return
                return

            for link in body['links']:
                if link['rel'] == 'next':
                    url = replace_endpoint(url, link['href'])
                    truncated = True

            for message in body['messages']:
                yield Message(self._conn, url='blah', content=message)

    @property
    def name(self):
        """The name of this queue"""
        return self._name
