# -*- coding: utf-8 -*-

from pyaloha.event import DictEvent, Event


# ALOHA:
# Sending when user type a request. It can be one event
# for every new letter in one word if user type not fast enough
#
# searchEmitResults [
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
        except KeyError:
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
            raise Exception('%s: Empty search query: %s' % (self.key, raw_query))

        self.query = query.strip()

        if not self.query:
            raise Exception(
                '%s: Trash query: %s' % (self.key, repr(raw_query))
            )

        try:
            self.gps = (float(self.data['posX']), float(self.data['posY']))
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
# ALOHA (iOS): Menu [ Button=Location Country=SA
# Language=ar-SA Orientation=Portrait ]
# Menu [ Country=IQ Language=ar-IQ Orientation=Portrait Traffic=Off ]
# Menu [ Country=CL Language=es-CL Orientation=Portrait TTS=On ]
# Country = 'RU'
# Language = 'ru-RU'
# Orientation = 'Portrait' or 'Landscape'
# Button =  'Location', 'Search', 'Expand', 'Point to point',
#           'Download maps', 'Bookmarks', 'Settings', 'Collapse',
#           'Share', 'Regular', 'Add place'
# Device type = 'iPhone' or 'iPad'
# Traffic = 'On' or 'Off'
# TTS = 'On' or 'Off'
'''
----------------------------------------
iOS:
Toolbar_click [ 
Country=RU
Language=ru-RU
Orientation=Portrait
button=point_to_point
]
Android:
Toolbar_click [ 
button=menu
]
----------------------------------------
iOS:
Toolbar_Menu_click [ 
Country=RU
Language=ru-RU
Orientation=Portrait
item=download_maps
]
Android:
Toolbar_Menu_click [ 
button=download_guides
]
----------------------------------------
old discovery button event
ios:
DiscoveryButton_Open [
Country=SA
Language=en-SA
Orientation=Portrait
network=none
]
android:
DiscoveryButton_Open [
network=wifi
]
----------------------------------------
'''


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
        'Toolbar_click',
        'Toolbar_Menu_click',
        'DiscoveryButton_Open'
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
        'Toolbar. Menu':        'Expand or Collapse',
        'DiscoveryButton_Open': 'discovery'
    }
    buttons_dict = {
        'menu':                 'Expand',
        'point_to_point':       'Point to point',
        'bookmarks':            'Bookmarks',
        'add_place':            'Add place',
        'download_maps':        'Download maps',
        'settings':             'Settings',
        'share_my_location':    'Share'
    }

    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__(*args, **kwargs)
        if self.key in self.keys_dict:
            self.button = self.keys_dict[self.key]
        elif self.key == 'Menu':
            self.button = self.data.get('Button', None)
        elif self.key == 'Toolbar_click':
            self.button = self.buttons_dict.get(
                self.data.get('button', None),
                self.data.get('button', None)
            )
        elif self.key == 'Toolbar_Menu_click':
            self.button = self.buttons_dict.get(
                self.data.get('button', self.data.get('item', None)),
                self.data.get('button', self.data.get('item', None))
            )
        else:
            self.button = None
        if self.button is not None:
            self.button = self.button.decode('utf-8').replace(u'\u0131', u'i').encode('utf-8')


# ALOHA:
# Send, when user click on sponsored icon in placepage
#
# Placepage_SponsoredActionButton_click
# [
# Country=RU
# Language=ru-RU
# Orientation=Portrait
# Provider=Thor
# category=3
# object_lat=55.70155054541721
# object_lon=37.52893103308179
# ]

class SponsoredClicks(DictEvent):
    keys = (
        'Placepage_SponsoredActionButton_click',
    )


# ALOHA:
# ios:
# Record recent track. When enabled, the duration is sent.
#
# Change recent track [
# Country=CN
# Language=zh-Hans-CN
# Orientation=Portrait
# Value={'1 hour(s)','2 hour(s)','6 hour(s)','12 hour(s)','24 hour(s)','Off'}
# ]
# android:
# One event for two actions in settings: record recent track
# and tracking statistics
#
# Statistics status changed  [
# Enabled={'true', 'false'}
# ]


class RecentTrack(DictEvent):
    STATISTICS_STATUS_CHANGED = 'Statistics status changed '
    STATISTICS_STATUS_CHANGED_GOOGLE = 'Statistics status changed google'
    STATISTICS_STATUS_CHANGED_NINESTORE = 'Statistics status changed nineStore'
    STATISTICS_STATUS_CHANGED_BLACKBERRY = 'Statistics status \
changed blackberry'
    STATISTICS_STATUS_CHANGED_APPCHINA = 'Statistics status changed appChina'
    STATISTICS_STATUS_CHANGED_SAMSUNG = 'Statistics status changed samsung'
    STATISTICS_STATUS_CHANGED_XIAOMI = 'Statistics status changed xiaomi'
    STATISTICS_STATUS_CHANGED_BAIDU = 'Statistics status changed baidu'
    STATISTICS_STATUS_CHANGED_AMAZON = 'Statistics status changed amazon'
    CHANGE_RECENT_TRACK = 'Change recent track'

    keys_dict = {
        STATISTICS_STATUS_CHANGED: 'default',
        STATISTICS_STATUS_CHANGED_GOOGLE: 'google',
        STATISTICS_STATUS_CHANGED_NINESTORE: 'ninestore',
        STATISTICS_STATUS_CHANGED_BLACKBERRY: 'blackberry',
        STATISTICS_STATUS_CHANGED_APPCHINA: 'appchina',
        STATISTICS_STATUS_CHANGED_SAMSUNG: 'samsung',
        STATISTICS_STATUS_CHANGED_XIAOMI: 'xiaomi',
        STATISTICS_STATUS_CHANGED_BAIDU: 'baidu',
        STATISTICS_STATUS_CHANGED_AMAZON: 'amazon',
        CHANGE_RECENT_TRACK: 'default'
    }

    keys = keys_dict.keys()

    def __init__(self, *args, **kwargs):
        super(RecentTrack, self).__init__(*args, **kwargs)
        self.merchant = self.keys_dict[self.key]
        self.value = self.data.get('Value')
        self.enabled = self.data.get('Enabled', self.value != 'Off')


# ALOHA:
# Сhoice of value for mobile internet in setting and in pop-up,
# when placepage was opened
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
        self.value = self.data.get('Value')


# ALOHA:
# ios only event, GDPR consent has been shown
# OnStart_MapsMeConsent_shown
# [
# Country=US
# Language=en-US
# Orientation=Portrait
# ]

class MapsMeConsentShown(DictEvent):
    keys = (
        'OnStart_MapsMeConsent_shown',
    )


# ALOHA:
# ios only event, GDPR consent has been accepted
# OnStart_MapsMeConsent_accepted
# [
# Country=BE
# Language=nl-BE
# Orientation=Landscape
# ]

class MapsMeConsentAccept(DictEvent):
    keys = (
        'OnStart_MapsMeConsent_accepted',
    )


# ALOHA:
# application has been installed
# android:
# $install
# [
# millisEpochInstalled=1230739200000
# package=com.mapswithme.maps.pro
# version=4.4.6-Preinstall
# versionCode=446
# ]
# ios:
# $install
# [
# CFBundleShortVersionString=8.6.0
# buildTimestampMillis=1545350812000
# installTimestampMillis=1546291840609
# updateTimestampMillis=0
# ]

class Install(DictEvent):
    keys = (
        '$install',
    )

    def __init__(self, *args, **kwargs):
        super(Install, self).__init__(*args, **kwargs)
        self.version = self.data.get(
            'CFBundleShortVersionString',
            self.data.get('version', u'0')
        )
        self.install_time = self.data.get(
            'installTimestampMillis',
            self.data.get('millisEpochInstalled', u'0')
        )


# ALOHA:
# sponsored category has been selected
# ios:
# Search_SponsoredCategory_selected
# [
# Country=RU
# Language=ru-RU
# Orientation=Portrait
# Provider=LuggageHero
# ]
# android:
# Search_SponsoredCategory_selected
# [
# provider=FIFA2018
# ]

class SponsoredCategoryClick(DictEvent):
    keys = (
        'Search_SponsoredCategory_selected',
    )

    def __init__(self, *args, **kwargs):
        super(SponsoredCategoryClick, self).__init__(*args, **kwargs)
        self.provider = self.data.get(
            'provider',
            self.data.get('Provider')
        ).lower()
