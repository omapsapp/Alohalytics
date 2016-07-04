from pyaloha.event import DictEvent

# Until April 2016 or smth like that:
#
# ALOHA: $GetUserMark [
# isLongPress=0
# lat=44.4269 lon=26.1682
# markType=POI metaData=1 name=2 type=building
# ]
#
# then:
#
# ALOHA: $SelectMapObject [
# bookmark=0 longTap=0 meters=32321
# title= types=building shop-mall
# ]
# <utc=0,lat=35.7128819,lon=139.7953817,acc=1.00>
#
# TODO: it will be nice to merge them some day in a one
# very happy event class. Now it only $SelectMapObject

# Event of the object selection with props:
# by_longtap: {True, False}
# object_types: {building, ..}
# user_info.get_location(): None or (lat, lon)
# user_info.uid
# user_info.os: {0 (Unknown), 1 (Android), 2 (iOS)}


class ObjectSelection(DictEvent):
    keys = (
        # '$GetUserMark',
        '$SelectMapObject',
    )

    def __init__(self, *args, **kwargs):
        super(ObjectSelection, self).__init__(*args, **kwargs)

        self.by_longtap = self.data['longTap'] != 0
        try:
            self.object_types = self.data.get('types', None).split(' ')
        except AttributeError:
            self.object_types = []
