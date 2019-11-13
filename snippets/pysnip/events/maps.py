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

    def __init__(self, *args, **kwargs):
        super(MapActionRequest, self).__init__(*args, **kwargs)

        self.action = self.data['action']
        self.scenario = self.data.get('scenario', None)
        self.init_from = self.data['from']


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
