from pyaloha.event import DictEvent

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
