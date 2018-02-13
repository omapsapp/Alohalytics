# -*- coding: utf-8 -*-

from pyaloha.event import Event, DictEvent


# ALOHA: searchEmitResults [
#   blida trib=8
# ]
#
# ALOHA (after Feb 2016): searchEmitResultsAndCoords [
#   posX=-71.9772 posY=-13.642 query=pizze results=10
#   Pizzeria|Restaurant|0   Don Angelo Pizzeria|Restaurant|0
#   viewportMaxX=-71.9639 viewportMaxY=-13.6282
#   viewportMinX=-71.998 viewportMinY=-13.663
# ]
#
# ALOHA (after Apr 2016): searchEmitResultsAndCoords [
#   locale=es_US
#   posX=-57.9893 posY=-33.1022
#   query=amor results=10
#   Doctor José G. Amorín|Calle|1   La Amarilla|place-neighbourhood|0
#   viewportMaxX=-57.9845 viewportMaxY=-33.101
#   viewportMinX=-57.9951 viewportMinY=-33.1085
# ]


class SearchResults(DictEvent):
    keys = (
        'searchEmitResults', 'searchEmitResultsAndCoords'
    )

    def __init__(self, *args, **kwargs):
        super(SearchResults, self).__init__(*args, **kwargs)

        try:
            raw_query = self.data['query']
        except KeyError as is_old_type_event:
            # TODO: investigate bug in c_api
            for raw_query, self.result_num in self.data.items():
                if raw_query:
                    break
        else:
            results = filter(None, self.data['results'].split())
            self.result_num = int(results[0])
            self.results = results[1:]

        query = raw_query.decode('utf8').encode('utf8')
        if not query:
            raise Exception('%s: Empty search query' % self.key)

        self.query = query.strip()

        if not self.query:
            raise Exception(
                '%s: Trash query: %s' % (self.key, repr(raw_query))
            )

        try:
            self.gps = map(
                float, (
                    self.data['posX'], self.data['posY']
                )
            )
        except (ValueError, KeyError):  # bad float, old type event
            self.gps = None

        try:
            self.viewport = {
                'maxx': float(self.data['viewportMaxX']),
                'maxy': float(self.data['viewportMaxY']),
                'minx': float(self.data['viewportMinX']),
                'miny': float(self.data['viewportMinY'])
            }
        except (ValueError, KeyError):  # bad float, old type event:
            self.viewport = None

        self.locale = self.data.get('locale')

        del self.data

    def process_me(self, processor):
        processor.process_search_results(self)

    def __dumpdict__(self):
        d = super(SearchResults, self).__basic_dumpdict__()
        d.update({
            'query': self.query,
            'gps': self.gps,
            'viewport': self.viewport,
            'locale': self.locale
        })
        return d


class GPSTracking(Event):
    keys = (
        'Flurry:logLocation', 'Framework:EnterBackground'
    )

    def __init__(self, *args, **kwargs):
        super(GPSTracking, self).__init__(*args, **kwargs)

        self.data_list = None

    def process_me(self, processor):
        processor.process_gps_tracking(self)

# ALOHA (Android): Menu. SettingsAndMore[]
# Menu. Point to point[]
# Menu. Downloader[]
# Menu. Share[]
# Menu. Add place.[]
# Toolbar. MyPosition[]
# Toolbar. Search[]
# Toolbar. Bookmarks[]
# Toolbar. Menu[]
# 
#
# ALOHA (iOS): Menu [ Button=Location Country=SA Language=ar-SA Orientation=Portrait ]
# Menu [ Country=IQ Language=ar-IQ Orientation=Portrait Traffic=Off ]
# Menu [ Country=CL Language=es-CL Orientation=Portrait TTS=On ]
# Country = 'RU'
# Language = 'ru-RU'
# Orientation = 'Portrait' or 'Landscape'
# Button =  'Location', 'Search', 'Expand', 'Point to point', 'Download maps', 
#           'Bookmarks', 'Settings', 'Collapse', 'Share', 'Regular', 'Add place'
# Device type = 'iPhone' or 'iPad'
# Traffic = 'On' or 'Off'
# TTS = 'On' or 'Off'

class Menu(DictEvent):
    keys = (
        'Menu', 
        'Menu. SettingsAndMore',
        'Menu. Point to point',
        'Menu. Downloader',
        'Menu. Share',
        'Menu. Add place.',
        'Toolbar. MyPosition',
        'Toolbar. Search',
        'Toolbar. Bookmarks',
        'Toolbar. Menu',
    )
    
    keys_dict = {
                    'Menu. SettingsAndMore':'Settings',
                    'Menu. Point to point': 'Point to point',
                    'Menu. Downloader':     'Download maps',
                    'Menu. Share':          'Share',
                    'Menu. Add place.':     'Add place',
                    'Toolbar. MyPosition':  'Location',
                    'Toolbar. Search':      'search',
                    'Toolbar. Bookmarks':   'Bookmarks',
                    'Toolbar. Menu':        'Expand or Collapse'
        }

    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__(*args, **kwargs)

        if self.key in self.keys_dict:
            self.button = self.keys_dict[self.key]
        elif self.key == 'Menu':
            try:
                self.button = self.data['Button']
            except KeyError:
                self.button = None
        else: 
            self.button = None

    def process_me(self, processor):
        processor.process_unspecified(self)


# ALOHA: 
# Country = 'RU'
# Language = 'ru-RU'
# Orientation = 'Portrait' or 'Landscape'
# provider = Thor
# object_lat
# 

class SponsoredClicks(DictEvent):
    keys = (
        'Placepage_SponsoredActionButton_click',
    )

    def __init__(self, *args, **kwargs):
        super(SponsoredClicks, self).__init__(*args, **kwargs)

    def process_me(self, processor):
        processor.process_unspecified(self)

# ALOHA: 
# ios:
# Change recent track [ 
# Country=CN 
# Language=zh-Hans-CN 
# Orientation=Portrait 
# Value={'1 hour(s)','2 hour(s)','6 hour(s)','12 hour(s)','24 hour(s)','Off'}
# ]
# android:
# Statistics status changed  [ 
# Enabled={'true', 'false'}
# ]

class RecentTrack(DictEvent):
    keys = (
        'Statistics status changed ',
        'Statistics status changed google',
        'Statistics status changed nineStore',
        'Statistics status changed blackberry',
        'Statistics status changed appChina',
        'Statistics status changed samsung',
        'Statistics status changed xiaomi',
        'Statistics status changed baidu',
        'Statistics status changed amazon',
        'Change recent track'
    )

    keys_dict = {
        'Statistics status changed ':           'default',
        'Statistics status changed google':     'google',
        'Statistics status changed nineStore':  'ninestore',
        'Statistics status changed blackberry': 'blackberry',
        'Statistics status changed appChina':   'appchina',
        'Statistics status changed samsung':    'samsung',
        'Statistics status changed xiaomi':     'xiaomi',
        'Statistics status changed baidu':      'baidu',
        'Statistics status changed amazon':     'amazon',
        'Change recent track': 'default'
    }

    def __init__(self, *args, **kwargs):
        super(RecentTrack, self).__init__(*args, **kwargs)
        self.merchant = self.keys_dict[self.key]
        if self.key == 'Change recent track':
            try:
                self.value = self.data['Value']
                if self.value == 'Off':
                    self.enabled = False
                else:
                    self.enabled = True
            except KeyError:
                self.enabled = None
        else:
            try:
                self.enabled = self.data['Enabled']
                if self.enabled:
                    self.value = 'On'
                else: 
                    self.value = 'Off'
            except KeyError:
                self.enabled = None

    def process_me(self, processor):
        processor.process_unspecified(self)


# ALOHA: 
# ios:
# Mobile Internet [ 
# Country=PL 
# Language=ru-UA 
# Orientation=Portrait 
# Value={Always,Ask,Never}
# ]
# android:


class MobileInternet(DictEvent):
    keys = (
        'Mobile Internet',
        )

    def __init__(self, *args, **kwargs):
        super(MobileInternet, self).__init__(*args, **kwargs)
        try:
            self.value = self.data['Value']
        except KeyError:
            self.value = None

    def process_me(self, processor):
        processor.process_unspecified(self)