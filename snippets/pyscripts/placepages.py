import collections
import functools
import operator

from pyaloha.base import DataAggregator as BaseDataAggregator
from pyaloha.base import StatsProcessor as BaseStatsProcessor

from pysnip.base import DataStreamWorker as BaseDataStreamWorker

import pysnip.events as events


UNIQ_USERS_PER_TAG_BY_MONTH_STR = """\
Monthly Unique Users per placepage category: %s
Category\tUsers
"""


def init_mau_per_tag(self, *args, **kwargs):
    self.monthly_users_per_type = collections.defaultdict(
        functools.partial(collections.defaultdict, set)
    )


class DataStreamWorker(BaseDataStreamWorker):
    __events__ = (
        events.placepage.ObjectSelection,
    )

    setup_shareable_data = init_mau_per_tag

    def process_unspecified(self, event):
        dte = event.event_time.dtime.date()
        if event.event_time.is_accurate:
            # there's a limitation to current serialization through json module
            # only common types are acceptable as keys to the serializable dict
            month = '%s%s' % (dte.year, dte.month)
            for tag in event.object_types:
                self.monthly_users_per_type[month][tag].add(
                    event.user_info.uid
                )


class DataAggregator(BaseDataAggregator):

    setup_shareable_data = init_mau_per_tag

    def aggregate(self, results):
        for month, otypes in results.monthly_users_per_type.iteritems():
            for ot, users in otypes.iteritems():
                self.monthly_users_per_type[month][ot].update(users)


class StatsProcessor(BaseStatsProcessor):
    def gen_stats(self):
        monthly_users_per_type = self.aggregator.monthly_users_per_type

        for month, otypes in monthly_users_per_type.iteritems():
            tags_by_popularity = sorted(
                ((ot, len(users)) for ot, users in otypes.iteritems()),
                key=operator.itemgetter(1)
            )

            yield UNIQ_USERS_PER_TAG_BY_MONTH_STR % month, tags_by_popularity
