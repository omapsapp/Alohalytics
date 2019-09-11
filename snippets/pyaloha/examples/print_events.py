"""cd ../../statistics/snippets/; ALOHA_DATA_DIR=/home/sites/alohalytics/ python2.7 pysnip/run.py print_events 20160301 20160310 1"""

from pyaloha.base import DataAggregator as BaseDataAggregator
from pyaloha.base import DataStreamWorker as BaseDataStreamWorker
from pyaloha.base import StatsProcessor as BaseStatsProcessor


class DataStreamWorker(BaseDataStreamWorker):
    def __init__(self, *args, **kwargs):
        super(DataStreamWorker, self).__init__(*args, **kwargs)

        self.events = []

    def process_unspecified(self, event):
        self.events.append(event)

    def pre_output(self):
        for event in self.events:
            event.__dumpdict__()

        del self.events
        del self.lost_data


class DataAggregator(BaseDataAggregator):
    def aggregate(self, results):
        for event in results.events:
            print(event)


class StatsProcessor(BaseStatsProcessor):
    def gen_stats(self, *args):
        return []