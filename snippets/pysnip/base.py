# The whole purpose of this module is to provide
# named Python aloha events from Maps.Me to a data stream worker
# and to define more specific callbacks

from pyaloha.base import DataStreamWorker as BaseDataStreamWorker

from pyaloha.event_factory import EventFactory

from pysnip.events.bookmark import BookmarkCreated, BookmarkAction, BookmarksDownloadedCatalogueOpen

from pysnip.events.misc import (
    GPSTracking, Menu, MobileInternet, RecentTrack,
    SearchResults, SponsoredClicks,
    MapsMeConsentShown, MapsMeConsentAccept, Install, SponsoredCategoryClick,
)

from pysnip.events.onstart import (
    AndroidVisibleLaunch, TechnicalLaunch,
    AndroidSessionStart, AndroidSessionEnd,
    DeviceInfo,
    IOSSessionStart, IOSSessionEnd, ColdStartupInfo, EnterBackground
)

from pysnip.events.placepage import (
    HotelClick, ObjectSelection, ObjectSelectionFromList, PlacepageShare,
    PlacepageFullOpen, SponsoredGallery
)

from pysnip.events.routing import (
    RouteEnd, RouteRequest, RouteStart, RouteTracking, RoutingBookmarksClick,
    RoutingPointAdd, RoutingSearch, TaxiRouteRequest, MapLayersActivate,
    RoutingTaxiOrder, RoutingTaxiInstall, RoutingManagerOpen,
)
from pysnip.events.ugc import (
    EditorEdit, EditorAddClick, UGCAuthError,
    UGCAuthSuccess, UGCReviewStart, UGCReviewSuccess,
    EditorAdd, UGCPushShown, UGCPushClick,
)
from pysnip.events.maps import (
    MapActionRequest, MapDownloadFinished, StartScreenDownloader,
    MapList, DownloaderBannerShow,
)
from pysnip.events.search import SearchFilterOpen, SearchFilterClick, SearchFilterApply
from pysnip.events.rendering import RenderingStats, GPU, VulkanForbidden


CUSTOM_EVENTS = (
    ObjectSelection,
    TechnicalLaunch, AndroidVisibleLaunch,
    AndroidSessionStart, AndroidSessionEnd,
    IOSSessionStart, IOSSessionEnd,
    HotelClick, ObjectSelectionFromList, PlacepageShare, PlacepageFullOpen, SponsoredGallery,
    SearchResults, GPSTracking,
    DeviceInfo,
    RouteRequest, RouteStart, RouteEnd, RouteTracking, TaxiRouteRequest,
    MapLayersActivate, RoutingBookmarksClick, RoutingPointAdd, RoutingSearch,
    MapActionRequest, MapDownloadFinished,
    Menu, SponsoredClicks, RecentTrack,
    EditorEdit, EditorAddClick, UGCReviewStart,
    UGCReviewSuccess, UGCAuthError, UGCAuthSuccess,
    RenderingStats, GPU,
    BookmarkCreated, BookmarkAction, BookmarksDownloadedCatalogueOpen, MobileInternet,
    RoutingTaxiOrder, RoutingTaxiInstall, RoutingManagerOpen, VulkanForbidden, StartScreenDownloader,
    ColdStartupInfo, EnterBackground,
    SearchFilterOpen, SearchFilterClick, SearchFilterApply,
    MapsMeConsentShown, MapsMeConsentAccept, Install, SponsoredCategoryClick,
    MapList, DownloaderBannerShow,
    EditorAdd, UGCPushShown, UGCPushClick,
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
