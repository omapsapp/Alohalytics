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


# ALOHA: Placepage_Hotel_book [
# Provider='Booking.com' 
# provider= 'Booking.com' //for android
# hotel=1474657 //booking hotel_id
# 
# hotel_location='35.7128819,139.7953817'
# hotel_lon='35.7128819'
# hotel_lat='139.7953817'
#
# user location:
# lon='35.7128819'
# lat='139.7953817'
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

# ALOHA: searchShowResult [ 
# pos=0 
# result=Ituzaing|Pueblo|0 
# ]
# result[0] = Name of POI
# result[1] = Type of POI on local language 
# result[2] = 1: Open pp from suggest; 0: Open pp from search without suggest
# result[3] = Osm tag. Will be add in task https://jira.mail.ru/browse/MAPSME-6699


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
    def fromSuggest(self):
        try:
            if self.data.get('result', None).split('|')[2] == 0:
                return False
            else:
                return True
        except IndexError:
            return False

    def __dumpdict__(self):
        d = super(DictEvent, self).__basic_dumpdict__()
        
        return d

# ALOHA: 
# iOS:
# Place page Share [ 
# Country=AZ 
# Language=ru-AZ 
# Orientation=Portrait 
# ]
# Ansroid: 
# PP. Share

class PlacepageShare(DictEvent):
    keys = (
        'PP. Share',
        'Place page Share',
    )

    def __dumpdict__(self):
        d = super(DictEvent, self).__basic_dumpdict__()
        
        return d
