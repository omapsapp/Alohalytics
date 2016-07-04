# Calculating the number of users
# active for the past three months or three weeks straight
# for every month or week in the given period

import collections
import itertools
import operator

from pyaloha.patterns.daily_over_fs import StatsSubscriber


THREE_MONTH_CORE_HEADER = """\
Counting users active 3 months straight
Month\tUsers
"""

THREE_WEEK_CORE_HEADER = """\
Counting users active 3 weeks straight
Week\tUsers
"""


# Base class for working with generic periods of usage
# pretty much defined through get_period_from_date

class CoreStats(StatsSubscriber):
    header = None
    period_depth = None

    def __init__(self):
        super(CoreStats, self).__init__()
        self.users_per_period = collections.defaultdict(set)

    def get_period_from_date(self, dte):
        raise NotImplementedError()

    def collect(self, item):
        dte, users = item
        period = self.get_period_from_date(dte)
        self.users_per_period[period].update(
            itertools.imap(
                operator.itemgetter(0),
                users
            )
        )

    def gen_stats(self):
        self.users_per_period = sorted(self.users_per_period.iteritems())

        period_numbers = range(
            self.period_depth - 1,
            len(self.users_per_period),
            +1
        )

        result_generator = (
            (
                self.users_per_period[period_num][0],
                self._n_deep_intersection_count(
                    period_num, n=self.period_depth
                )
            )
            for period_num in period_numbers
        )

        return self.header, result_generator

    def _n_deep_intersection_count(self, period_num, n=3):
        user_set = self.users_per_period[period_num][1]
        for prev_n in range(period_num - 1, period_num - n, -1):
            user_set = user_set.intersection(
                self.users_per_period[prev_n][1]
            )
        return len(user_set)


class ThreeWeekCoreStats(CoreStats):
    header = THREE_WEEK_CORE_HEADER
    period_depth = 3

    def get_period_from_date(self, dte):
        return dte.isocalendar()[:2]


class ThreeMonthCoreStats(CoreStats):
    header = THREE_MONTH_CORE_HEADER
    period_depth = 3

    def get_period_from_date(self, dte):
        return (dte.year, dte.month)
