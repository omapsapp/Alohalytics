import collections

from pyaloha.base import DataAggregator as BaseDataAggregator
from pyaloha.base import StatsProcessor as BaseStatsProcessor
from pysnip.base import DataStreamWorker as BaseDataStreamWorker
import pysnip.events as events

def init_collections(self):
    self.gpus = collections.Counter()


class DataStreamWorker(BaseDataStreamWorker):
    __events__ = (
        events.rendering.GPU,
    )

    setup_shareable_data = init_collections

    def process_unspecified(self, event):
        self.gpus[event.gpu] += 1

            
class DataAggregator(BaseDataAggregator):
    setup_shareable_data = init_collections

    def aggregate(self, results):
        self.gpus.update(results.gpus)


class StatsProcessor(BaseStatsProcessor):
    def process_stats(self):
        with open("gpu_rating.csv", "w") as text_file:
            text_file.write("GPU;Sessions Count;\n")
            for gpu, cnt in self.aggregator.gpus.most_common():
                text_file.write("{0};{1};\n".format(gpu, cnt))

    def gen_stats(self):
        return []
