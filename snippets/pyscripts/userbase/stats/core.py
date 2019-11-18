# Counts users
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


# Base class for working with generic time units (week, month, day)
# of usage pretty much defined through get_unit_id_from_date

class CoreStats(StatsSubscriber):
    header = None
    period_depth = None

    def __init__(self):
        super(CoreStats, self).__init__()
        self.users_per_timeunit = collections.defaultdict(set)

    def get_timeunit_from_date(self, dte):
        raise NotImplementedError()

    def collect(self, item):
        dte, users = item
        tunit_id = self.get_timeunit_from_date(dte)
        self.users_per_timeunit[tunit_id].update(
            itertools.imap(
                operator.itemgetter(0),
                users
            )
        )

    def gen_stats(self):
        self.users_per_timeunit = sorted(
            self.users_per_timeunit.iteritems()
        )

        timeunit_range = range(
            self.period_depth - 1,
            len(self.users_per_timeunit)
        )

        result_generator = (
            (
                self.users_per_timeunit[timeunit_num][0],
                self._n_deep_intersection_count(timeunit_num)
            )
            for timeunit_num in timeunit_range
        )

        return self.header, result_generator

    def _n_deep_intersection_count(self, timeunit_num):
        core_range = range(
            timeunit_num - self.period_depth + 1,
            timeunit_num
        )
        user_set = self.users_per_timeunit[timeunit_num][1]
        for prev_n in core_range:
            user_set = user_set.intersection(
                self.users_per_timeunit[prev_n][1]
            )
        return len(user_set)


class ThreeWeekCoreStats(CoreStats):
    header = THREE_WEEK_CORE_HEADER
    period_depth = 3

    def get_timeunit_from_date(self, dte):
        # (ISO year, ISO week number)
        return dte.isocalendar()[:2]


class ThreeMonthCoreStats(CoreStats):
    header = THREE_MONTH_CORE_HEADER
    period_depth = 3

    def get_timeunit_from_date(self, dte):
        return (dte.year, dte.month)