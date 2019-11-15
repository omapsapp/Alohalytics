from pyaloha.event import DictEvent, Event


class RouteDictEvent(DictEvent):

    mode_alliases = {
        'astar-bidirectional-pedestrian': 'pedestrian',
        'astar-bidirectional-bicycle': 'bicycle',
        'astar-bidirectional-car': 'vehicle',
        'pedestrian': 'pedestrian',
        'bicycle': 'bicycle',
        'vehicle': 'vehicle',
        'mixed-car': 'vehicle',
        'astar-bidirectional-transit': 'transit',
        'subway': 'transit'
    }

    def __init__(self, *args, **kwargs):
        super(RouteDictEvent, self).__init__(*args, **kwargs)
        mode = self.data.get('router', self.data.get('name', None)).lower()
        self.mode = self.mode_alliases.get(mode, mode)


# ALOHA: Routing_CalculatingRoute [
#   distance=51797.4 elapsed=6.56531
#   finalLat=49.45913 finalLon=35.11263
#   name=vehicle result=NoError
#   startDirectionX=0 startDirectionY=0
#   startLat=49.55215 startLon=34.52105
# ]
#
# Event for route creation with specific props:
# mode: {'vehicle', 'pedestrian'}
# start: (lat, lon)
# destination: None or (lat, lon)
# status: {None, 'NoError', 'Cancelled'}
# distance:

class RouteRequest(RouteDictEvent):
    keys = (
        'Routing_CalculatingRoute',
    )

    def __init__(self, *args, **kwargs):
        super(RouteRequest, self).__init__(*args, **kwargs)

        self.start = self.user_info.get_location() or (
            self.data['startLat'], self.data['startLon']
        )

        try:
            self.destination = (
                self.data['finalLat'], self.data['finalLon']
            )
        except KeyError:
            self.destination = None

        self.status = self.data.get('result')
        self.distance = self.data.get('distance')


# Event for a start of the route with specific props
# with no specific fields
# Android: Routing. Start []
# iOS: Point to point Go [
# Country = 'AR'
# Language = 'ru-UA'
# Orientation = 'Portrait'
# Value: {'From my position', 'Point to point', 'To my position'}
# ]
"""
--------------------------------------------------
Android:
Point to point Go [
Value=From my position 
]
iOS:
Point to point Go [
Country=CU
Language=es-ES
Orientation=Portrait
Value=From my position 
]
--------------------------------------------------
Android:
Routing_Route_start [ 
mode=vehicle
traffic=0
]
iOS:
Routing_Route_start [ 
Country=RU
Language=ru-RU
Orientation=Portrait
Traffic=0
mode=vehicle
]
--------------------------------------------------
"""


class RouteStart(Event):
    keys = (
        'Routing. Start',
        'Point to point Go',
        'Routing_Route_start',
    )

    def __init__(self, *args, **kwargs):
        super(RouteStart, self).__init__(*args, **kwargs)

        try:
            self.traffic = self.data.get('traffic', self.data.get('Traffic', None))
            self.mode = self.data.get('mode', None)
        except AttributeError:
            self.traffic = None
            self.mode = None


# ALOHA: RouteTracking_RouteClosing [
#   distance=513244 percent=0.197765
#   rebuildCount=0 router=vehicle
# ] <utc=0,lat=44.4369109,lon=8.9513113,acc=1.00>
#
# ALOHA: RouteTracking_ReachedDestination [
#   passedDistance=3.1224
#   rebuildCount=0 router=vehicle
# ]

class RouteEnd(RouteDictEvent):
    keys = (
        'RouteTracking_RouteClosing',
        'RouteTracking_ReachedDestination'
    )

    def __init__(self, *args, **kwargs):
        super(RouteEnd, self).__init__(*args, **kwargs)

        try:
            self.rebuild_count = int(self.data['rebuildCount'])
        except KeyError:
            self.rebuild_count = None

        self.distance_done = self.data.get(
            'distance', self.data.get('passedDistance', None)
        )

        self.percent = float(self.data.get('percent', 100))


# ALOHA: RouteTracking_PercentUpdate [
#   percent=75.3459
# ] <utc=0,lat=-9.9709619,lon=-67.8104598,acc=1.00>

class RouteTracking(RouteDictEvent):
    keys = (
        'RouteTracking_PercentUpdate',
    )

    def __init__(self, *args, **kwargs):
        super(RouteTracking, self).__init__(*args, **kwargs)

        self.percent = float(self.data.get('percent', 100))

# ALOHA: Routing_Build_Taxi [ provider=Uber ]
# Event send, when user calculate route on taxi with specific property
# provider = {'Uber', 'Yandex'}


class TaxiRouteRequest(DictEvent):
    keys = (
        'Routing_Build_Taxi',
    )

    def __init__(self, *args, **kwargs):
        super(TaxiRouteRequest, self).__init__(*args, **kwargs)
        self.mode = 'taxi'
        self.provider = self.data.get('provider', 'Unknown')


# ALOHA:
# Old event, change state of traffic. Not UI change.
# UI change included, but event can be send, without users actions.
# $TrafficChangeState [ state=WaitingData ]
#
# New event, change state of any layers in application (now traffic and subway)
# Not UI change.
# UI change included, but event can be send, without users actions.
# Map_Layers_activate
# [
# Name=subway
# status=success
# ]
"""
--------------------------------------------------
Android:
Map_Layers_activate
[
Name=traffic
status=DISABLED
]
--------------------------------------------------
iOS:
Map_Layers_activate [ 
Country=DE
Language=de-DE
Orientation=Portrait
name=traffic
status=success
]
--------------------------------------------------
"""


class MapLayersActivate(DictEvent):
    keys = (
        '$TrafficChangeState',
        'Map_Layers_activate'
    )

    state_alliases = {
        'success': 'enabled'
    }

    def __init__(self, *args, **kwargs):
        super(MapLayersActivate, self).__init__(*args, **kwargs)
        if self.key == '$TrafficChangeState':
            self.action = self.data.get('state', 'unknown').lower()
            self.name = 'traffic'
        elif self.key == 'Map_Layers_activate':
            self.name = self.data.get('Name', self.data.get('name', None))
            self.action = self.data.get('status', 'unknown').lower()

            if self.action in self.state_alliases:
                self.action = self.state_alliases[self.action]


# Event send, when user click on bookmark button after build route
# or after start planning route
# ALOHA:
# ios: Routing_Bookmarks_click [
# Country=IQ
# Language=ar-IQ
# Orientation=Portrait
# mode=planning
# ]
# android: Routing_Bookmarks_click [
# mode=onroute
# ]


class RoutingBookmarksClick(DictEvent):
    keys = (
        'Routing_Bookmarks_click',
    )

    def __init__(self, *args, **kwargs):
        super(RoutingBookmarksClick, self).__init__(*args, **kwargs)
        self.mode = self.data.get('mode')


# Event send, when user added point to route. It can be from placepage
# or on planning page
# ALOHA:
# ios: Routing_Point_add [
# Country=PK
# Language=en-PK
# Orientation=Portrait
# method: {'planning_pp', 'outside_pp'}
# mode: {'planning', 'onroute', None}
# type: {'start', 'finish', 'inner'}
# value: {'gps', 'point'}
# ]
#
# android: Routing_Point_add [
# method: {'planning_pp', 'outside_pp'}
# mode: {'planning', 'onroute', None}
# type: {'start', 'finish', 'inner'}
# value: {'gps', 'point'}
# ]


class RoutingPointAdd(DictEvent):
    keys = (
        'Routing_Point_add',
    )

    def __init__(self, *args, **kwargs):
        super(RoutingPointAdd, self).__init__(*args, **kwargs)
        self.mode = self.data.get('mode', 'onroute')
        self.method = self.data.get('method', 'outside_pp')
        self.type = self.data.get('type', 'unknown')
        self.value = self.data.get('value', 'unknown')


# Event send, when user click on search button after build route
# or after start planning route
# ALOHA:
# ios: Routing_Search_click [
# Country=PK
# Language=en-PK
# Orientation=Portrait
# mode: {'planning', 'onroute'}
# ]
#
# android: Routing_Search_click [
# mode: {'planning', 'onroute'}
# ]


class RoutingSearch(DictEvent):
    keys = (
        'Routing_Search_click',
    )

    def __init__(self, *args, **kwargs):
        super(RoutingSearch, self).__init__(*args, **kwargs)
        self.mode = self.data.get('mode', 'onroute')


# User clicked on button "order taxi" in placepage.
# If he has a taxi application, Routing_Taxi_order will be send,
# if he hasn't, Routing_Taxi_install will be send
# ALOHA:
# android:
# Routing_Taxi_order
# [
# from_lat=-11.989991400000001
# from_lon=-77.0691169
# provider=Uber
# to_lat=-12.054727786240294
# to_lon=-77.12083299028994
# ]
# <utc=1514758162000,lat=-11.9897872,lon=-77.0688617,acc=53.09,spd=0.00,src=Unk>
#
# Routing_Taxi_install
# [
# from_lat=25.129832000000004
# from_lon=55.194609
# provider=Uber
# to_lat=25.118169236941394
# to_lon=55.20048286915184
# ]
# <utc=1514758496000,lat=25.1330818,lon=55.1935794,acc=41.00,spd=0.00,src=GPS>
# ios:
# Routing_Taxi_order
# [
# Country=ME
# Language=en-ME
# Orientation=Portrait
# Provider=Uber
# from_location=-22.91784411764045,-43.18100036125927
# to_location=-22.98487999999999,-43.198601
# ]
# <utc=1514758289528,lat=-22.9179772,lon=-43.1809275,acc=65.00,alt=82.03,vac=10.00>
#
# Routing_Taxi_install
# [
# Country=PL
# Language=ru-BY
# Orientation=Portrait
# Provider=Uber
# from_location=52.22150277351236,21.01252097638418
# to_location=52.24291852638538,21.00276292117509
# ]
# <utc=1514759092002,lat=52.2215027,lon=21.0125208,acc=10.00,alt=110.92,vac=6.00,bea=0.0000000,spd=0.00>

class RoutingTaxiOrder(DictEvent):
    keys = (
        'Routing_Taxi_order',
        'Routing_Taxi_install'
    )

    def __init__(self, *args, **kwargs):
        super(RoutingTaxiOrder, self).__init__(*args, **kwargs)

        if self.key == 'Routing_Taxi_order':
            self.action = 'order'
        else:
            self.action = 'install'
        self.provider = self.data.get(
            'provider',
            self.data.get('Provider', None)
        )
        self.from_location = self.data.get('from_location', None)
        if self.from_location:
            self.from_location = tuple(
                float(item)
                for item in self.from_location.split(',')
            )
        else:
            self.from_location = (
                float(self.data.get('from_lat', 0)),
                float(self.data.get('from_lon', 0))
            )

        self.to_location = self.data.get('to_location', None)
        if self.to_location:
            self.to_location = tuple(
                float(item)
                for item in self.to_location.split(',')
            )
        else:
            self.to_location = (
                float(self.data.get('to_lat', 0)),
                float(self.data.get('to_lon', 0))
            )
