# To run the script do smth like this:
# ./pysnip/run.py userbase 20150601 20160610 > userbase.stats
#
# Technically this is the main module for a task of
# calculating different period-based (days, weeks, months) statistics
# for the users of Maps.Me
# Scheme is based on pyaloha.patterns.daily_over_fs pattern
# Stats subscribers (actual business logic of stats calculation)
# are located in stats subpackage

import collections

from pyaloha.patterns.daily_over_fs import (
    DataAggregator as DailyAggregator,
    StatsProcessor as DailyStatsProcessor
)
from pyaloha.protocol import day_serialize, SerializableSet

from pysnip.base import DataStreamWorker as BaseDataStreamWorker
import pysnip.events as events

from .stats.core import ThreeMonthCoreStats, ThreeWeekCoreStats
from .stats.dau import DAUStats, OSDAUStats, NumOfDaysStats
from .stats.mau import MAUStats


# Data stream worker processes app launch events
# using basic event scheme (process_unspecified callback)
# The only problem worth mentioning is matching TechnicalLaunch events
# (that are not necessarily visible) for Android to visible UI
# launch events

class DataStreamWorker(BaseDataStreamWorker):
    __events__ = (
        events.onstart.TechnicalLaunch,
        events.onstart.AndroidVisibleLaunch
    )

    def __init__(self):
        super(DataStreamWorker, self).__init__()

        self.data_per_days = collections.defaultdict(dict)
        self.count_events = 0
        self.android_visible_launches = collections.defaultdict(set)

    def process_unspecified(self, event):
        self.count_events += 1
        dtime = event.event_time.dtime
        uid = event.user_info.uid
        if event.event_time.is_accurate:
            dt = day_serialize(dtime)
            if isinstance(event, events.onstart.AndroidVisibleLaunch):
                self.android_visible_launches[dt].add(uid)
            else:
                # TODO: agg
                self.data_per_days[dt][uid] = event.user_info
        elif uid not in self.data_per_days:
            self.lost_data.add(uid)

    def is_invisible_android_launch(self, dte, uid, user_info):
        return (
            user_info.is_on_android() and
            uid not in self.android_visible_launches[dte]
        )

    # TODO: to think about more clear scheme of providing results
    # from worker to aggregator
    # For now worker destroys non-visible android launches
    # and deletes temporary structures
    def pre_output(self):
        for dte, users in self.data_per_days.iteritems():
            for uid, uinfo in users.items():
                if self.is_invisible_android_launch(dte, uid, uinfo):
                    del users[uid]
        del self.android_visible_launches


class DataAggregator(DailyAggregator):
    pass


class StatsProcessor(DailyStatsProcessor):
    subscribers = (
        DAUStats, OSDAUStats, NumOfDaysStats,
        MAUStats,
        ThreeMonthCoreStats, ThreeWeekCoreStats
    )
