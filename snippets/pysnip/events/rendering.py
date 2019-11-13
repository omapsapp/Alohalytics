import collections

from pyaloha.event import DictEvent

# ALOHA: RenderingStats [
# version=8.5.0
# device=iPhone 6s
# gpu=Apple A9
# api=OpenGLES3
# width=1024
# height=768
# minFrameTime=1
# maxFrameTime=455
# avgFrameTime=80
# slowFrames=38
# frames=126
# viewportMinLat=55.7631
# viewportMinLon=37.6581
# viewportMaxLat=55.7587
# viewportMaxLon=37.6481
# ]


class RenderingStats(DictEvent):
    keys = (
        'RenderingStats',
    )

    def __init__(self, *args, **kwargs):
        super(RenderingStats, self).__init__(*args, **kwargs)

        self.version = self.data.get('version', 'Unknown')
        self.device = self.data.get('device', 'Unknown')
        self.gpu = self.data.get('gpu', 'Unknown')
        self.api = self.data.get('api', 'Unknown')
        w = int(self.data.get('width', 0))
        h = int(self.data.get('height', 0))
        self.width = max(w, h)
        self.height = min(w, h)
        self.frame_data = collections.Counter()
        self.frame_data['min_frame_time_ms'] = int(self.data.get('minFrameTime', 1000000000))
        self.frame_data['max_frame_time_ms'] = int(self.data.get('maxFrameTime', 0))
        self.frame_data['avg_frame_time_ms'] = int(self.data.get('avgFrameTime', 0))
        self.frame_data['slow_frames_count'] = int(self.data.get('slowFrames', 0))
        self.frame_data['frames_count'] = int(self.data.get('frames', 0))
        self.frame_data['counter'] = 1

        try:
            self.viewport_min_lat_lon = (
                float(self.data['viewportMinLat']),
                float(self.data['viewportMinLon'])
            )
        except KeyError:
            self.viewport_min_lat_lon = None

        try:
            self.viewport_max_lat_lon = (
                float(self.data['viewportMaxLat']),
                float(self.data['viewportMaxLon'])
            )
        except KeyError:
            self.viewport_max_lat_lon = None


class GPU(DictEvent):
    keys = (
        'GPU',
    )

    def __init__(self, *args, **kwargs):
        super(GPU, self).__init__(*args, **kwargs)

        self.gpu = self.data.keys()[0]
