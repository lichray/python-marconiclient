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
from urlparse import urlparse


class TestClientException(testtools.TestCase):

    def test_exception(self):
        # Basic instantiation and inheritance check

        ex = ClientException("Something bad happened")
        self.assertTrue(isinstance(ex, Exception))

    #TODO Use dependency injection to mock HTTP(S)Client
    def test_connection(self):

        """
        conn = Connection(
            auth_endpoint="https://identity.api.rackspacecloud.com/v2.0",
            client_id=str(uuid.uuid4()),
            endpoint="http://localhost:8888/v1/12345",
            user="", key="")

        """

        conn = Connection(
            auth_endpoint="https://identity.api.rackspacecloud.com/v2.0",
            client_id=str(uuid.uuid4()),
            endpoint="http://166.78.143.130/v1/12345",
            user="", key="")

        conn.connect(token='blah')

        def create_worker(queue_name):
            return conn.create_queue(queue_name)

        def post_worker(queue):
            return queue.post_message('test_message', 10)

        def delete_worker(queue_name):
            conn.delete_queue(queue_name)
            return queue_name

        pool = GreenPool(1000)

        def on_message_posted(greenthread):
            msg = greenthread.wait()
            print msg._href

        def on_queue_created(greenthread):
            queue = greenthread.wait()
            print queue.name

            for x in range(0, 10):
                gt = pool.spawn(post_worker, queue)
                gt.link(on_message_posted)

        queue_names = ["queue-" + str(x) for x in xrange(0, 5)]

        for queue_name in queue_names:
            gt = pool.spawn(create_worker, queue_name)
            gt.link(on_queue_created)

        pool.waitall()

        def delete_worker(queue_name):
            conn.delete_queue(queue_name)
            print "Queue:", queue_name, " deleted"

        for queue in conn.get_queues():
            gt = pool.spawn_n(delete_worker, queue.name)

        print "Waiting for everything to finish"
        pool.waitall()
        print "Done"
