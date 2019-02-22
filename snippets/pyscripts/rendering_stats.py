import collections

from pyaloha.base import DataAggregator as BaseDataAggregator
from pyaloha.base import StatsProcessor as BaseStatsProcessor
from pysnip.base import DataStreamWorker as BaseDataStreamWorker
import pysnip.events as events
import csv

def init_collections(self):
    self.devices = collections.defaultdict(collections.Counter)


def merge(frame_data_in, frame_data_out):
    t = frame_data_out['avg_frame_time_ms'] * frame_data_out['frames_count']
    t += frame_data_in['avg_frame_time_ms'] * frame_data_in['frames_count']
    frames_count = frame_data_out['frames_count'] + frame_data_in['frames_count']
    if frames_count > 0:
        frame_data_out['avg_frame_time_ms'] = int(t / frames_count)
    frame_data_out['frames_count'] = frames_count
    frame_data_out['min_frame_time_ms'] = min(frame_data_out['min_frame_time_ms'], frame_data_in['min_frame_time_ms'])
    frame_data_out['max_frame_time_ms'] = max(frame_data_out['max_frame_time_ms'], frame_data_in['max_frame_time_ms'])
    frame_data_out['slow_frames_count'] += frame_data_in['slow_frames_count']
    frame_data_out['counter'] += max(1, frame_data_in['counter'])


class DataStreamWorker(BaseDataStreamWorker):
    __events__ = (
        events.rendering.RenderingStats,
    )

    setup_shareable_data = init_collections

    def process_unspecified(self, event):
        resolution = '{0}x{1}'.format(event.width, event.height)
        k = (event.device, event.gpu, resolution, event.version, event.api)
        frame_data = self.devices[k]
        merge(event.frame_data, frame_data)

    def pre_output(self):
        self.devices = self.devices.items()

            
class DataAggregator(BaseDataAggregator):
    setup_shareable_data = init_collections

    def aggregate(self, results):
        for k, frame_data in results.devices:
            f = self.devices[tuple(k)]
            merge(frame_data, f)


class StatsProcessor(BaseStatsProcessor):
    def process_stats(self):
        with open("rendering_stats_by_devices.csv", "w") as csvfile:
            w = csv.writer(csvfile)
            w.writerow(['Count', 'Device', 'GPU', 'Resolution', 'Version', 
                        'API', 'Avg Frame Time (ms)', 'Min Frame Time (ms)', 
                        'Max Frame Time (ms)', 'Slow Frames Percent'])
            for (device, gpu, resolution, version, api), frame_data in self.aggregator.devices.iteritems():
                slow_frames_percent = 100.0 * frame_data['slow_frames_count'] / frame_data['frames_count']
                w.writerow([frame_data['counter'], device.encode('utf-8'), gpu.encode('utf-8'),
                           resolution, version, api, frame_data['avg_frame_time_ms'],
                           frame_data['min_frame_time_ms'], frame_data['max_frame_time_ms'],
                           slow_frames_percent])

    def gen_stats(self):
        return []
