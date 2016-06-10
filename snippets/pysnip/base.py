from pyaloha.base import DataStreamWorker as BaseDataStreamWorker

from pyaloha.event_factory import EventFactory

from pysnip.events.misc import GPSTracking, SearchResults
from pysnip.events.onstart import AndroidVisibleLaunch, TechnicalLaunch
from pysnip.events.placepage import ObjectSelection
from pysnip.events.routing import RouteEnd, RouteRequest, RouteStart, RouteTracking


CUSTOM_EVENTS = (
    ObjectSelection,
    TechnicalLaunch, AndroidVisibleLaunch,
    SearchResults, GPSTracking,
    RouteRequest, RouteStart, RouteEnd, RouteTracking,
)


class DataStreamWorker(BaseDataStreamWorker):
    def __init__(self, event_factory=EventFactory(CUSTOM_EVENTS)):
        super(DataStreamWorker, self).__init__(
            event_factory=event_factory
        )

    def process_search_results(self, event):
        pass

    def process_gps_tracking(self, event):
        pass

    def process_routing(self, event):
        pass
