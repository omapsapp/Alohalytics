from pyaloha.event import DictEvent


# ALOHA: Downloader_Map_action [
# action=update from=downloader is_auto=No scenario=update
# ]
# User action with an mwm file in app
# Its properties are:
# action: {update,}
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


# ALOHA: $OnMapDownloadFinished [
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
