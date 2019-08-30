# The whole purpose of this module is to provide
# named Python aloha events from Maps.Me to a data stream worker
# and to define more specific callbacks

from pyaloha.base import DataStreamWorker as BaseDataStreamWorker

from pyaloha.event_factory import EventFactory

from pysnip.events.bookmark import BookmarkCreated

from pysnip.events.misc import (
    GPSTracking, Menu, MobileInternet, RecentTrack,
    SearchResults, SponsoredClicks
)

from pysnip.events.onstart import (
    AndroidVisibleLaunch, TechnicalLaunch,
    AndroidSessionStart, AndroidSessionEnd,
    DeviceInfo,
    IOSSessionStart, IOSSessionEnd
)

from pysnip.events.placepage import (
    BookmarkAction,
    HotelClick, ObjectSelection, ObjectSelectionFromList, PlacepageShare
)

from pysnip.events.routing import (
    RouteEnd, RouteRequest, RouteStart, RouteTracking, RoutingBookmarksClick,
    RoutingPointAdd, RoutingSearch, TaxiRouteRequest, TrafficState
)
from pysnip.events.ugc import (
    EditorStart, EditorAddClick, UGCAuthError,
    UGCAuthSuccess, UGCReviewStart, UGCReviewSuccess
)
from pysnip.events.maps import MapActionRequest, MapDownloadFinished
from pysnip.events.rendering import RenderingStats, GPU


CUSTOM_EVENTS = (
    ObjectSelection, BookmarkAction,
    TechnicalLaunch, AndroidVisibleLaunch,
    AndroidSessionStart, AndroidSessionEnd,
    IOSSessionStart, IOSSessionEnd,
    HotelClick, ObjectSelectionFromList, PlacepageShare,
    SearchResults, GPSTracking,
    DeviceInfo,
    RouteRequest, RouteStart, RouteEnd, RouteTracking, TaxiRouteRequest,
    TrafficState, RoutingBookmarksClick, RoutingPointAdd, RoutingSearch,
    MapActionRequest, MapDownloadFinished,
    Menu, SponsoredClicks, RecentTrack,
    EditorStart, EditorAddClick, UGCReviewStart,
    UGCReviewSuccess, UGCAuthError, UGCAuthSuccess,
    RenderingStats, GPU,
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
