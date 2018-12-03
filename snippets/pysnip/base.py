# The whole purpose of this module is to provide
# named Python aloha events from Maps.Me to a data stream worker
# and to define more specific callbacks

from pyaloha.base import DataStreamWorker as BaseDataStreamWorker

from pyaloha.event_factory import EventFactory

from pysnip.events.misc import GPSTracking, SearchResults
from pysnip.events.onstart import AndroidVisibleLaunch, TechnicalLaunch
from pysnip.events.placepage import ObjectSelection
from pysnip.events.routing import (
    RouteEnd, RouteRequest, RouteStart, RouteTracking
)
from pysnip.events.maps import MapActionRequest, MapDownloadFinished
from pysnip.events.rendering import RenderingStats, GPU


CUSTOM_EVENTS = (
    ObjectSelection,
    TechnicalLaunch, AndroidVisibleLaunch,
    SearchResults, GPSTracking,
    RouteRequest, RouteStart, RouteEnd, RouteTracking,
    MapActionRequest, MapDownloadFinished,
    RenderingStats, GPU,
)


class DataStreamWorker(BaseDataStreamWorker):
    def __init__(self, event_factory=EventFactory(CUSTOM_EVENTS)):
        super(DataStreamWorker, self).__init__(
            event_factory=event_factory
        )

    def process_search_results(self, event):
        self.process_unspecified(event)

    def process_gps_tracking(self, event):
        self.process_unspecified(event)

    def process_routing(self, event):
        self.process_unspecified(event)
