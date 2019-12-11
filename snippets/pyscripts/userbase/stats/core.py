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

USAGES_PER_WEEK_HEADER = """\
Counting user per week entries
Week\tUsers\tEntries
"""

USAGES_PER_DAY_HEADER = """\
Counting user per day entries
Day\tUsers\tEntries
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


# Does not inherit `CoreStats` since logic differs a lot
class EntriesPerWeekStats(StatsSubscriber):

    def __init__(self):
        super(EntriesPerWeekStats, self).__init__()

        self.header = USAGES_PER_WEEK_HEADER
        self.results = collections.defaultdict(dict)

    def get_timeunit_from_date(self, dte):
        return dte.isocalendar()[:2]

    def collect(self, item):
        dte, users_complicated_list = item
        user_ids_in_dte = [one_list[0] for one_list in users_complicated_list]
        current_week = self.get_timeunit_from_date(dte)
        # For element, call its inner method
        for user in user_ids_in_dte:
            results_current_user = self.results[user]
            results_current_user[current_week] = results_current_user.get(current_week, 0) + 1

    def gen_stats(self):
        result = list()
        for user_id, dict_with_date_and_entries in self.results.iteritems():
            for year_week_tuple, value in dict_with_date_and_entries.iteritems():
                to_add = ('-'.join(map(str, year_week_tuple)), user_id, value)
                result.append(to_add)
        return self.header, result
