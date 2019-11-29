from pyaloha.event import DictEvent
from pysnip.osm_tags import TaggedOSMObject

# ALOHA:
# Sending, when user create bookmark from placepage

# ios
# Bookmark. Bookmark created [
# Country=NZ
# Language=fr-FR
# Orientation=Portrait
# ]
# android
# Bookmark. Bookmark created [
# Count=1
# ]


class BookmarkCreated(DictEvent):
    keys = (
        'Bookmark. Bookmark created',
    )

    def __init__(self, *args, **kwargs):
        super(BookmarkCreated, self).__init__(*args, **kwargs)

        self.count = int(self.data.get('Count', 1))


# ALOHA:
# Bookmarks_Bookmark_action
# [
# action=create
# lat=4.68445
# lon=-74.0603
# tags=highway-residential,psurface-paved_good
# ]

class BookmarkAction(DictEvent):
    keys = (
        'Bookmarks_Bookmark_action',
    )

    def __init__(self, *args, **kwargs):
        super(BookmarkAction, self).__init__(*args, **kwargs)
        self.action = self.data.get('action')
        self.coord = (self.data.get('lat', 0), self.data.get('lon', 0))
        self.tags = self.data.get('tags').split(' ')

    @property
    def object_types(self):
        try:
            return self.data['tags'].split(',')
        except KeyError:
            return []

    @property
    def numeric_types(self):
        try:
            return TaggedOSMObject(self.data['tags'].split(','))
        except KeyError:
            return None

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


'''
----------------------------------------
iOS:
Bookmarks_Downloaded_Catalogue_open [ 
Country=XK
Language=sq-XK
Orientation=Portrait
from=Downloaded
]
----------------------------------------
Android:
Bookmarks_Downloaded_Catalogue_open [ 
]
----------------------------------------
'''


class BookmarksDownloadedCatalogueOpen(DictEvent):
    keys = (
        'Bookmarks_Downloaded_Catalogue_open',
    )

    def __init__(self, *args, **kwargs):
        super(BookmarksDownloadedCatalogueOpen, self).__init__(*args, **kwargs)
        self.source = self.data.get('from')
