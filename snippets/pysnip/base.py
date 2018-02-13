# The whole purpose of this module is to provide
# named Python aloha events from Maps.Me to a data stream worker
# and to define more specific callbacks

from pyaloha.base import DataStreamWorker as BaseDataStreamWorker

from pyaloha.event_factory import EventFactory

from pysnip.events.misc import (
    GPSTracking, SearchResults, Menu, SponsoredClicks, 
    RecentTrack, MobileInternet
)
from pysnip.events.onstart import AndroidVisibleLaunch, TechnicalLaunch, DeviceInfo
from pysnip.events.placepage import ObjectSelection, HotelClick, ObjectSelectionFromList, PlacepageShare
from pysnip.events.routing import (
    RouteEnd, RouteRequest, RouteStart, RouteTracking, TaxiRouteRequest, 
    Traffic, RoutingBookmarksClick, RoutingPointAdd, RoutingSearch
)
from pysnip.events.maps import MapActionRequest, MapDownloadFinished
from pysnip.events.bookmark import BookmarkCreated
from pysnip.events.ugc import EditorAdd, EditorAddClick, EditorEdit, UGCReviewStart, UGCReviewSuccess, UGCAuthError, UGCAuthSuccess


CUSTOM_EVENTS = (
    ObjectSelection, HotelClick, ObjectSelectionFromList, PlacepageShare,
    TechnicalLaunch, AndroidVisibleLaunch, DeviceInfo,
    SearchResults, GPSTracking,
    RouteRequest, RouteStart, RouteEnd, RouteTracking, TaxiRouteRequest, 
    Traffic, RoutingBookmarksClick, RoutingPointAdd, RoutingSearch,
    MapActionRequest, MapDownloadFinished, 
    Menu, SponsoredClicks, RecentTrack,
    EditorAdd, EditorAddClick, EditorEdit, UGCReviewStart, UGCReviewSuccess, UGCAuthError, UGCAuthSuccess,
    BookmarkCreated, MobileInternet
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
