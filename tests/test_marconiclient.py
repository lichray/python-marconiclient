# Copyright (c) 2010-2012 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import testtools
from marconiclient import *
from eventlet import GreenPool
import uuid



class TestClientException(testtools.TestCase):

    def test_exception(self):
        # Basic instantiation and inheritance check

        ex = ClientException("Something bad happened")
        self.assertTrue(isinstance(ex, Exception))


    #TODO Use dependency injection to mock HTTP(S)Client
    def test_connection(self):
        conn = Connection(auth_url="https://identity.api.rackspacecloud.com/v2.0",
                          client_id=str(uuid.uuid4()),
                          endpoint="http://166.78.143.130:80/v1/12345",
                          user="", key="", token='blah')

        conn.connect()

        """
        def create_worker(queue_name):
            return conn.create_queuget_queuee(queue_name, 1000)

        def delete_worker(queue_name):
            conn.delete_queue(queue_name)
            return queue_name

        pool = GreenPool()

        def on_queue_created(greenthread):
            queue = greenthread.wait()
            print queue.name

        queue_names = [str(x) for x in xrange(0,10000)]

        for queue_name in queue_names:
            gt = pool.spawn(create_worker, queue_name)
            gt.link(on_queue_created)

        pool.waitall()
        """
        queue = conn.create_queue('test_queue', ttl=100)

        for x in range(0, 25):
            print "Posting..."
            msg = queue.post_message("XXX:"+str(x), 500)


        msgs = queue.claim_messages(ttl=30, grace=100)

        """
        for msg in q1.get_messages():
            pass # print "Body:", msg['body'], msg['ttl'], msg['id']
        """

        """
        for queue in conn.list_queues():
            print queue
        """
        """
        queue = conn.create_queue('test_queue_whatever', 50)
        msg_body = {"username":"buford", "age":32}
        msg = queue.post_message(msg_body, 10000)

        msg.delete()
        """

        # msg = msg.read()

        """
        for queue in pool.imap(create_worker, queue_names):
            print "Created: ", queue.name
        """

        """
        for queue_name in pool.imap(delete_worker, queue_names):
            print "Deleted: ", queue_name
        """
