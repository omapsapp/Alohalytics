# -*- coding: utf-8 -*-
from pyaloha.event import DictEvent


# ALOHA:
# Sending on action with maps. Action one of this:
# update — update map;
# download — download new map;
# delete — delete old map;
# retry — retry downloading after error;
# cancel — abort downloading;
# explore — click show region on the map;
# Event can be call from:
# map — drag map to new location and download map;
# downloader — choose map in list of regions and make some action;
# placepage — download map from placepage of city or country
# Downloader_Map_action [
# action=update from=downloader is_auto=No scenario=update
# ]
# User action with an mwm file in app
# Its properties are:
# action: {update, download, delete, retry, cancel, explore}
# from: {map, downloader, placepage}
# user_info.get_location(): None or (lat, lon)
# user_info.uid
# user_info.os: {0 (Unknown), 1 (Android), 2 (iOS)}

class MapActionRequest(DictEvent):
    keys = (
        'Downloader_Map_action',
    )
    is_auto = {
        'Yes': True,
        'No': False,
        'false': False,
        'true': True,
        'unknown': 'unknown'
    }

    def __init__(self, *args, **kwargs):
        super(MapActionRequest, self).__init__(*args, **kwargs)

        self.action = self.data.get('action').lower()
        self.scenario = self.data.get('scenario')
        self.init_from = self.data.get('from')
        self.is_auto = self.is_auto.get(self.data.get('is_auto', 'unknown'))


# ALOHA:
# Event send after map download complete
# $OnMapDownloadFinished [
# name=Morocco_Rabat-Sale-Zemmour-Zaer
# option=MapWithCarRouting status=ok version=160317
# ]

class MapDownloadFinished(DictEvent):
    keys = (
        '$OnMapDownloadFinished',
    )

    def __init__(self, *args, **kwargs):
        super(MapDownloadFinished, self).__init__(*args, **kwargs)

        self.name = self.data['name']
        self.version = int(self.data['version'])
        self.status = self.data.get('status')


# ALOHA: Downloader_OnStartScreen_auto_download
# Send, when maps updates automatically on start screen
# [
# map_data_size:=5.0
# ]
# ALOHA: Downloader_OnStartScreen_manual_download
# Send, when maps updates manually on start screen
# [
# map_data_size:=77.0
# ]

class StartScreenDownloader(DictEvent):
    keys = (
        'Downloader_OnStartScreen_auto_download',
        'Downloader_OnStartScreen_manual_download'
    )

    def __init__(self, *args, **kwargs):
        super(StartScreenDownloader, self).__init__(*args, **kwargs)

        if self.key == 'Downloader_OnStartScreen_auto_download':
            self.is_auto = True
        else:
            self.is_auto = False

        self.map_data_size = int(self.data.get('map_data_size', 0))

# ALOHA: Downloader_Map_list [
# AvailableStorageSpace=763142144
# DownloadedMaps=Bolivia_North:180126;World:180126;WorldCoasts:180126;
# ]
# Regular event with actual map on users device
# Its properties are:
# AvailableStorageSpace: bytes
# DownloadedMaps: map:version

class MapList(DictEvent):
    keys = (
        'Downloader_Map_list',
    )

    def __init__(self, *args, **kwargs):
        super(MapList, self).__init__(*args, **kwargs)

        self.storage = int(self.data.get('AvailableStorageSpace', 0))
        downloaded_maps = self.data.get('DownloadedMaps', '')
        if len(downloaded_maps) > 0:
            self.maps = dict(map(
                lambda a: a.split(":"),
                downloaded_maps.strip(";").split(";")
            ))
        else:
            self.maps = {}


# ALOHA: Downloader_Banner_show
# Banner in downloader
# ios:
# [
# Country=DK
# Language=da-DK
# Orientation=Landscape
# Provider=MapsMeGuides
# from=map
# ]
# android:
# [
# from=map
# provider=Megafon
# ]


class DownloaderBannerShow(DictEvent):
    keys = (
        'Downloader_Banner_show',
    )

    def __init__(self, *args, **kwargs):
        super(DownloaderBannerShow, self).__init__(*args, **kwargs)

        self.provider = self.data.get('Provider', self.data.get('provider'))
        self.place = self.data.get('from')
