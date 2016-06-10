import collections

from pysnip.base import DataStreamWorker as BaseDataStreamWorker

import pysnip.events as events

from pyaloha.patterns.daily_over_fs import (
    DataAggregator as DailyAggregator,
    StatsProcessor as DailyStatsProcessor
)

from pyaloha.protocol import day_serialize

from .stats.dau import DAUStats, OSDAUStats, NumOfDaysStats
from .stats.core import ThreeMonthCoreStats, ThreeWeekCoreStats


class DataStreamWorker(BaseDataStreamWorker):
    __events__ = (
        events.onstart.TechnicalLaunch,
        events.onstart.AndroidVisibleLaunch
    )

    def __init__(self):
        super(DataStreamWorker, self).__init__()

        self.data_per_days = collections.defaultdict(dict)
        self.lost_users = set()
        self.count_events = 0
        self.android_vstarts = collections.defaultdict(set)

    def process_unspecified(self, event):
        self.count_events += 1
        dtime = event.event_time.dtime
        uid = event.user_info.uid
        if event.event_time.is_accurate:
            dt = day_serialize(dtime)
            if isinstance(event, events.onstart.AndroidVisibleLaunch):
                self.android_vstarts[dt].add(uid)
            else:
                # TODO: agg
                self.data_per_days[dt][uid] = event.user_info.stripped()
        else:
            self.lost_users.add(uid)

    def pre_output(self):
        for dte, users in self.data_per_days.iteritems():
            for uid, uinfo in users.items():
                if uinfo.os == 1 and uid not in self.android_vstarts[dte]:
                    del users[uid]
        del self.android_vstarts


class DataAggregator(DailyAggregator):
    pass


class StatsProcessor(DailyStatsProcessor):
    subscribers = (
        DAUStats, OSDAUStats, NumOfDaysStats,
        ThreeMonthCoreStats, ThreeWeekCoreStats
    )
