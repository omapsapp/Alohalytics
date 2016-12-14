import collections
import functools
import operator

from pyaloha.base import DataAggregator as BaseDataAggregator
from pyaloha.base import StatsProcessor as BaseStatsProcessor
from pyaloha.protocol import SerializableSet

from pysnip.base import DataStreamWorker as BaseDataStreamWorker
from pysnip.osm_tags import get_groups_by_tag

import pysnip.events as events


UNIQ_USERS_PER_TAG_BY_MONTH_STR = """\
Monthly Unique Users per placepage category: %s
Category\tUsers
"""


def init_mau_per_tag(self, *args, **kwargs):
    self.monthly_users_per_type = collections.defaultdict(
        functools.partial(collections.defaultdict, SerializableSet)
    )
    self.monthly_hits_per_type = collections.defaultdict(
        collections.Counter
    )
    self.lost_data = SerializableSet()


class DataStreamWorker(BaseDataStreamWorker):
    __events__ = (
        events.placepage.ObjectSelection,
    )

    setup_shareable_data = init_mau_per_tag

    def process_unspecified(self, event):
        dte = event.event_time.dtime.date()
        if event.event_time.is_accurate:
            # There's a limitation to current serialization through json module:
            # only common types are acceptable as keys in serializable dict.
            month = '%s-%s' % (dte.year, dte.month)
            set_groups = []
            for tag in event.object_types:
                for group in get_groups_by_tag(tag):
                    if group not in set_groups:
                        set_groups.append(group)

                        self.monthly_users_per_type[month][group].add(
                            event.user_info.uid
                        )
                        self.monthly_hits_per_type[month][group] += 1

                self.monthly_users_per_type[month][tag].add(
                    event.user_info.uid
                )
                self.monthly_hits_per_type[month][tag] += 1


class DataAggregator(BaseDataAggregator):

    setup_shareable_data = init_mau_per_tag

    def aggregate(self, results):
        for month, otypes in results.monthly_users_per_type.iteritems():
            for ot, users in otypes.iteritems():
                self.monthly_users_per_type[month][ot].update(users)

        for month, otypes in results.monthly_hits_per_type.iteritems():
            for ot, cnt in otypes.iteritems():
                self.monthly_hits_per_type[month][ot] += cnt


class StatsProcessor(BaseStatsProcessor):
    def gen_stats(self):
        monthly_users_per_type = self.aggregator.monthly_users_per_type

        for month, otypes in monthly_users_per_type.iteritems():
            hits = self.aggregator.monthly_hits_per_type[month]
            tags_by_popularity = sorted(
                ((ot, len(users), hits[ot])
                 for ot, users in otypes.iteritems()),
                key=operator.itemgetter(1)
            )

            yield UNIQ_USERS_PER_TAG_BY_MONTH_STR % month, tags_by_popularity
