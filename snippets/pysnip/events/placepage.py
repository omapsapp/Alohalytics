from pyaloha.event import DictEvent

# Event tracked, when user select object on the map.
# It can be POI, search result or any another place.
#
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
        '$GetUserMark',
        '$SelectMapObject',
    )

    __slots__ = tuple()

    @property
    def by_longtap(self):
        return self.data['longTap'] != 0

    @property
    def bookmark(self):
        try:
            return int(self.data['bookmark'])
        except KeyError:
            return -1

    @property
    def object_types(self):
        try:
            return self.data.get('types', None).split(' ')
        except AttributeError:
            return []

    def __dumpdict__(self):
        d = super(DictEvent, self).__basic_dumpdict__()
        d.update({
            'by_longtap': self.by_longtap,
            'object_types': self.object_types
        })
        return d


# Click on the Booking.com button in hotel placepage.
#
# ALOHA:
# ios:
# Placepage_Hotel_book [
# Country=RU
# Language=ru-RU
# Orientation=Portrait
# Provider=Booking.com
# hotel=2569121
# hotel_location=59.93650856114328,30.36258884044429
# ]
# android:
# Placepage_Hotel_book [
# hotel=40649
# hotel_lat=53.622651546550166
# hotel_lon=-6.921042106457378
# provider=Booking.Com
# ]


class HotelClick(DictEvent):
    keys = (
        'Placepage_Hotel_book',
    )

    __slots__ = tuple()

    @property
    def provider(self):
        try:
            return self.data['provider'].lower()
        except KeyError:
            return self.data['Provider'].lower()

    @property
    def hotel_location(self):
        hotel_location = self.data.get('hotel_location')
        if hotel_location:
            return tuple(map(
                float, (hotel_location.split(','))
            ))
        else:
            return (
                float(self.data.get('hotel_lat')),
                float(self.data.get('hotel_lon'))
            )

    @property
    def hotel_id(self):
        return self.data.get('hotel')


# Event tracked, when user select object in list of search results.
#
# ALOHA: searchShowResult [
# pos=0
# result=Ituzaing|Pueblo|0
# ]
# result[0] = Name of place
# result[1] = Type of place on local language
# result[2] = 1: Open pp from suggest; 0: Open pp from search without suggest
# result[3] = Osm tag. Will be add in task jira.mail.ru/browse/MAPSME-6699


class ObjectSelectionFromList(DictEvent):
    keys = (
        'searchShowResult',
    )

    __slots__ = tuple()

    @property
    def position(self):
        return self.data['pos']

    @property
    def object_type(self):
        try:
            return self.data.get('result', None).split('|')[1]
        except IndexError:
            return 'Unknown'

    @property
    def name(self):
        try:
            return self.data.get('result', None).split('|')[0]
        except IndexError:
            return None

    @property
    def fromsuggest(self):
        try:
            if self.data.get('result', None).split('|')[2] == '0':
                return False
            else:
                return True
        except IndexError:
            return False

    def __dumpdict__(self):
        return super(DictEvent, self).__basic_dumpdict__()

# Click on share button in placepage. There is no have any special properties.
# ALOHA:
# iOS:
# Place page Share [
# Country=AZ
# Language=ru-AZ
# Orientation=Portrait
# ]
# Android:
# PP. Share


class PlacepageShare(DictEvent):
    keys = (
        'PP. Share',
        'Place page Share',
    )

    def __dumpdict__(self):
        return super(DictEvent, self).__basic_dumpdict__()
