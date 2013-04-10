class Stats(object):

    def __init__(self, stats):
        """
        :param: stats Statistics about a queue
        """
        self._message_stats = stats['messages']
        self._action_stats = stats['actions']

    @property
    def messages(self):
        """Returns statistics about the queue's messages"""
        return self._message_stats

    @property
    def actions(self):
        """Returns statistics about the queue's actions"""
        return self._action_stats
