# Monthly based user stats

import collections
import itertools
import operator

from pyaloha.patterns.daily_over_fs import StatsSubscriber


MAU_HEADER = """\
Calculating MAU
Month\tUsers
"""


class MAUStats(StatsSubscriber):
    def __init__(self):
        super(MAUStats, self).__init__()

        self.MAU = collections.defaultdict(set)

    def collect(self, item):
        dte, users = item
        month = (dte.year, dte.month)
        self.MAU[month].update(
            itertools.imap(operator.itemgetter(0), users)
        )

    def gen_stats(self):
        result_generator = (
            (m, len(uids))
            for m, uids in self.MAU.iteritems()
        )
        return MAU_HEADER, sorted(result_generator)
