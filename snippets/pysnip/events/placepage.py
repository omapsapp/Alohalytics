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

    __slots__ = tuple()

    @property
    def object_location(self):
        return (
            self.user_info.lat,
            self.user_info.lon
        )

    @property
    def by_longtap(self):
        return self.data['longTap'] != 0

    @property
    def object_types(self):
        try:
            return self.data.get('types', None).split(' ')
        except AttributeError:
            return []

    @property
    def title(self):
        return self.data.get('title', None)

    def __dumpdict__(self):
        d = super(DictEvent, self).__basic_dumpdict__()
        d.update({
            'by_longtap': self.by_longtap,
            'object_types': self.object_types,
            'object_location': self.object_location
        })
        return d


class BookmarkAction(DictEvent):
    keys = (
        'Bookmarks_Bookmark_action',
    )

    __slots__ = tuple()

    @property
    def action(self):
        return self.data['action']

    @property
    def object_types(self):
        try:
            return self.data['tags'].split(',')
        except KeyError:
            return []

    @property
    def object_location(self):
        try:
            return float(self.data['lat']), float(self.data['lon'])
        except KeyError:  # old event
            return None

    def __dumpdict__(self):
        d = super(DictEvent, self).__basic_dumpdict__()
        d.update({
            'action': self.action,
            'object_types': self.object_types,
            'object_location': self.object_location
        })
        return d
