import collections

from alohalytics import ResultCollector as BaseResultCollector
from alohalytics import StreamProcessor as BaseProcessor
from alohalytics import day_deserialize, day_serialize

import events


class StreamProcessor(BaseProcessor):
    __events__ = (events.onstart.Launch,)

    def __init__(self):
        self.visit_days = collections.defaultdict(set)
        self.lost_users = set()
        self.count_events = 0

    def process_unspecified(self, event):
        self.count_events += 1
        dtime = event.event_time.dtime
        if event.event_time.is_accurate:
            self.visit_days[day_serialize(dtime)].add(event.user_info.uid)
        else:
            self.lost_users.add(event.user_info.uid)

    def finish(self):
        pass


class ResultCollector(BaseResultCollector):
    def __init__(self):
        super(ResultCollector, self).__init__()

        self.total_count = 0
        self.lost_users = set()
        self.agg_visit_days = collections.defaultdict(set)

        self.subscribers = (DAUStats, NumOfDaysStats, ThreeMonthCoreStats)

    def add(self, processor_results):
        self.total_count += processor_results.count_events

        self.lost_users.update(processor_results.lost_users)
        for dte, uids in processor_results.visit_days.iteritems():
            self.agg_visit_days[day_deserialize(dte)].update(uids)

    def gen_stats(self):
        print 'Lost users', len(self.lost_users)
        self.lost_users.clear()

        procs = tuple(s() for s in self.subscribers)

        for item in sorted(self.agg_visit_days.iteritems()):
            for p in procs:
                p.collect(item)
            # uids set: do not need that, 2 times less memory consumption
            item[1].clear()

        for p in procs:
            yield p.gen_stats()


class StatsProcessor(object):
    def collect(self, item):
        raise NotImplementedError()

    def gen_stats(self):
        raise NotImplementedError()


class DAUStats(StatsProcessor):
    def __init__(self):
        self.DAU = []

    def collect(self, item):
        dte, uids = item
        self.DAU.append((day_serialize(dte), len(uids)))

    def gen_stats(self):
        return 'DAU\nDate\tUsers', self.DAU


class NumOfDaysStats(StatsProcessor):
    def __init__(self):
        self.days_per_user = collections.Counter()

    def collect(self, item):
        dte, uids = item
        for u in uids:
            self.days_per_user[u] += 1

    def gen_stats(self):
        users_per_day = collections.Counter()
        for u, cnt in self.days_per_user.iteritems():
            for i in range(1, cnt + 1):
                users_per_day[i] += 1
        return 'Days\tUsers', sorted(users_per_day.items())


class ThreeMonthCoreStats(StatsProcessor):
    def __init__(self):
        self.users_per_month = collections.defaultdict(set)

    def collect(self, item):
        dte, uids = item
        self.users_per_month[(dte.year, dte.month)].update(uids)

    def gen_stats(self):
        self.users_per_month = sorted(self.users_per_month.iteritems())
        return '3M Core\nMonth\tUsers', (
            (self.users_per_month[m_count][0], len(
                self.users_per_month[m_count][1]
                .intersection(
                    self.users_per_month[m_count - 1][1]
                )
                .intersection(
                    self.users_per_month[m_count - 2][1]
                )
            ))
            for m_count in range(3, len(self.users_per_month), +1)
        )
