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

TOURISTS_CORE_HEADER = """\
Counting tourists core
Users\tIs_tourist
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


class TouristsCore(StatsSubscriber):
    """
    Find active tourists among users using particular pattern of behaviour.
    A user is considered to be active if he follows all points:
        1) His total activity throughout a year since
           first entrance cannot exceed 30 days, for each one-year period;
        2) His total activity in a row cannot exceed 3 weeks, for each activity row;

    Since alohalytics processes data `row-by-row`, this implementation must be a
    single pass algorithm.
    """

    def __init__(self):
        super(TouristsCore, self).__init__()
        self.header = TOURISTS_CORE_HEADER
        # TODO: maybe create separate class `UserCounter` that implements all the logic?
        # Implements (1) from algorithm
        self.total_in_year_counter = dict()
        # Implements (2) from algorithm
        self.in_row_counter = dict()
        # The last day user have been seen
        self.last_day = dict()
        # The first day in year counter
        self.first_year_day = dict()
        # For results
        self.results = dict()
        # TODO: for debug only
        self.dtes = []

    def update_user_status(self, user,
                           max_days_per_year=30, max_days_in_row=14):
        """
        Called each time when any counter is being reset.
        Checks if the user meets behaviour requirements and marks it correspondingly.

        :param user: user ID
        :param max_days_per_year: maximum number of entries in a year
        :param max_days_in_row: maximum number of entries in a row
        :return:
        """
        if (self.total_in_year_counter[user] > max_days_per_year) or \
                (self.in_row_counter[user] > max_days_in_row):
            self.results[user] = False

    def __update_year_counter__(self, user, dte):
        """
        Updates year counter and checks whether user has exceeded year limit

        :param user: user ID
        :param dte: datetime object from Aloha
        :return:
        """
        # Seen for the first time
        DAYS_IN_YEAR = 365
        if self.total_in_year_counter.get(user) is None:
            self.total_in_year_counter[user] = 1
            self.first_year_day[user] = dte
            self.results[user] = True
            return
        if abs(self.first_year_day[user] - dte).days < DAYS_IN_YEAR:
            self.total_in_year_counter[user] += 1
        else:
            # Need to reset counter
            self.update_user_status(user)
            self.total_in_year_counter[user] = 0
            self.first_year_day[user] = dte

    def __update_user_last_day__(self, user, dte):
        self.last_day[user] = dte

    def __update_user_in_row_counter__(self, user, dte, MAX_DELTA=2):
        # Seen for the first time
        if self.in_row_counter.get(user) is None:
            self.in_row_counter[user] = 1
            return
        # need to check whether user hasn't been active for more than MAX_DELTA days
        last_date = self.last_day[user]
        if abs(dte - last_date).days > MAX_DELTA:
            # If more, reset counter
            # But before reset, check if user is still 'good' one
            self.update_user_status(user)
            self.in_row_counter[user] = 0
        else:
            # Else, increment counter
            self.in_row_counter[user] += 1

    # NOTE: dte's come sorted
    def collect(self, item):
        dte, users_complicated_list = item
        # Alohalytics gives data day-by-day
        user_ids_in_day = [one_list[0] for one_list in users_complicated_list]
        for user in user_ids_in_day:
            # If user hasn't been seen before
            if self.results.get(user, -1) == -1:
                # Consider him as 'good' user by default
                self.results[user] = True
            # If user is proved to be non-touristic, ignore him
            if not self.results.get(user, True):
                continue
            self.__update_year_counter__(user, dte)
            self.__update_user_in_row_counter__(user, dte)
            self.__update_user_last_day__(user, dte)

    def gen_stats(self):
        return self.header, self.results.items()
