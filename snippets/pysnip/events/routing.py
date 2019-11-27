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
        self.setup_mode()

    def setup_mode(self):

        mode = self.data.get(
            'router', self.data.get('name', '')
        ).lower()
        if mode in self.mode_alliases:
            self.mode = self.mode_alliases[mode]
        else: 
            self.mode = mode

    def process_me(self, processor):
        processor.process_routing(self)


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

        # TODO: not sure if try/except is better than dict.get()
        try:
            self.start = (
                float(self.data['startLat']), float(self.data['startLon'])
            )
        except KeyError:
            self.start = self.user_info.get_location()

        try:
            self.destination = (
                float(self.data['finalLat']), float(self.data['finalLon'])
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


class RouteStart(DictEvent):
    keys = (
        'Routing. Start',
        'Point to point Go',
        'Routing_Route_start',
    )

    def __init__(self, *args, **kwargs):
        super(RouteStart, self).__init__(*args, **kwargs)

        self.traffic = self.data.get('traffic', self.data.get('Traffic', None))
        self.mode = self.data.get('mode', None)


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
# ----------------------------------------
# android:
# Routing_Taxi_order
# [
# from_lat=-11.989991400000001
# from_lon=-77.0691169
# provider=Uber
# to_lat=-12.054727786240294
# to_lon=-77.12083299028994
# ]
# ----------------------------------------
# iOS:
# Routing_Taxi_order [
# Country=RU
# Language=ru-RU
# Orientation=Portrait
# Provider=Uber
# from_location=38.76902613113875,-9.128432964183331
# to_location=38.70397092919239,-9.183689275262424
# ]
# <utc=1570315025249,lat=38.7689933,lon=-9.1284489,acc=65.00,alt=97.76,vac=10.00>
# ----------------------------------------
# <utc=1514758162000,lat=-11.9897872,lon=-77.0688617,acc=53.09,spd=0.00,src=Unk>
class RoutingTaxiOrder(DictEvent):
    keys = (
        'Routing_Taxi_order',
    )

    def __init__(self, *args, **kwargs):
        super(RoutingTaxiOrder, self).__init__(*args, **kwargs)

        self.provider = self.data.get('provider')
        if self.provider is None:
            self.provider = self.data.get('Provider')

        self.from_location = self.data.get('from_location')
        if self.from_location is None:
            self.from_location = (float(self.data.get('from_lat')), float(self.data.get('from_lon')))
        else:
            self.from_location = tuple(float(item) for item in self.from_location.split(','))

        self.to_location = self.data.get('to_location')
        if self.to_location is None:
            self.to_location = (float(self.data.get('to_lat')), float(self.data.get('to_lon')))
        else:
            self.to_location = tuple(float(item) for item in self.to_location.split(','))
            

'''
ALOHA:
----------------------------------------
Android
Routing_Taxi_install [
from_lat=25.129832000000004
from_lon=55.194609
provider=Uber
to_lat=25.118169236941394
to_lon=55.20048286915184
]
<utc=1570313390000,lat=55.9240682,lon=37.7227406,acc=41.01,bea=194.1323698,spd=0.28,src=Unk>
----------------------------------------
iOS:
Routing_Taxi_install [
Country=RU
Language=en-RU
Orientation=Portrait
Provider=Maxim
from_location=41.70279812560331,44.79204432960243
to_location=41.74415752670366,44.77275956252782
]
<utc=1570313490116,lat=41.7028373,lon=44.7921091,acc=65.00,alt=439.38,vac=10.00>
----------------------------------------
'''
class RoutingTaxiInstall(DictEvent):
    keys = (
        'Routing_Taxi_install',
    )

    def __init__(self, *args, **kwargs):
        super(RoutingTaxiInstall, self).__init__(*args, **kwargs)
        
        self.provider = self.data.get('provider')
        if self.provider is None:
            self.provider = self.data.get('Provider')

        self.from_location = self.data.get('from_location')
        if self.from_location is None:
            self.from_location = (float(self.data.get('from_lat')), float(self.data.get('from_lon')))
        else:
            self.from_location = tuple(float(item) for item in self.from_location.split(','))

        self.to_location = self.data.get('to_location', None)
        if self.to_location is None:
            self.to_location = (float(self.data.get('to_lat')), float(self.data.get('to_lon')))
        else:
            self.to_location = tuple(float(item) for item in self.to_location.split(','))
            

# ALOHA:
# ios: Routing_RouteManager_open [
# Country=PK
# Language=en-PK
# Orientation=Portrait
# ]

class RoutingManagerOpen(DictEvent):
    keys = (
        'Routing_RouteManager_open',
    )

    def __init__(self, *args, **kwargs):
        super(RoutingManagerOpen, self).__init__(*args, **kwargs)

    def process_me(self, processor):
        processor.process_routing(self)
