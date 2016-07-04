# User stats calculated on a daily basis

import collections
import itertools
import operator

from pyaloha.patterns.daily_over_fs import StatsSubscriber
from pyaloha.protocol import day_serialize


DAU_HEADER = '''\
Calculating DAU
Date\tUsers
'''

DAU_BY_OS_HEADER = '''\
Calculating DAU by OS
Date\tAndroid\tiOS'
'''

DAYS_ACTIVE_HEADER = '''\
Calculating days users were active (total, not straight)
'Days\tUsers'
'''


class DAUStats(StatsSubscriber):
    def __init__(self):
        super(DAUStats, self).__init__()

        self.DAU = []

    def collect(self, item):
        dte, users = item
        self.DAU.append(
            (day_serialize(dte), len(users))
        )

    def gen_stats(self):
        return DAU_HEADER, self.DAU


# DAU by OS

class OSDAUStats(StatsSubscriber):
    def __init__(self):
        super(OSDAUStats, self).__init__()

        self.DAU = []

    def collect(self, item):
        dte, users = item

        os_types = itertools.imap(
            lambda x: x[1]['os'],
            users
        )
        ordered_counted_os_types = map(
            operator.itemgetter(1),
            sorted(
                collections.Counter(os_types).iteritems()
            )
        )
        self.DAU.append(
            [day_serialize(dte)] + ordered_counted_os_types
        )

    def gen_stats(self):
        return DAU_BY_OS_HEADER, self.DAU


# How many users were active 1 day, 2 days, 3 days and so on
# NOTE: if a user was active 2 days, he will be calculated in both
# 1 and 2 days active periods

class NumOfDaysStats(StatsSubscriber):
    def __init__(self):
        super(NumOfDaysStats, self).__init__()

        self.days_per_user = collections.Counter()

    def collect(self, item):
        dte, users = item
        self.days_per_user.update(
            itertools.imap(operator.itemgetter(0), users)
        )

    def gen_stats(self):
        users_per_day = collections.Counter()
        for u, cnt in self.days_per_user.iteritems():
            users_per_day.update(range(1, cnt + 1))
        return DAYS_ACTIVE_HEADER, sorted(users_per_day.iteritems())
