# -*- coding: utf-8 -*-

from pyaloha.event import DictEvent


# ALOHA: 
# Android: 
# Search_Filter_Open [ 
# category=hotel 
# ]
# iOS:
# Search_Filter_Open [ 
# Country=CA 
# Language=en-CA 
# Orientation=Portrait 
# category=hotel 
# ]


class SearchFilterOpen(DictEvent):
    keys = (
        'Search_Filter_Open', 
    )

    def __init__(self, *args, **kwargs):
        super(SearchFilterOpen, self).__init__(*args, **kwargs)

        self.category = self.data.get('category')

    def process_me(self, processor):
        processor.process_unspecified(self)



# ALOHA: 
# Android: [ 
# category=hotel 
# date=check_in 
# ]
# iOS:
# Search_Filter_Click [ 
# Country=NL 
# Language=nl-NL 
# Orientation=Portrait 
# category=hotel 
# price_category=2 
# ]


class SearchFilterClick(DictEvent):
    keys = (
        'Search_Filter_Click', 
    )

    filter_types = (
        'date',
        'rating',
        'class',
        'price_category',
        'type',
        'room'
        )

    def __init__(self, *args, **kwargs):
        super(SearchFilterClick, self).__init__(*args, **kwargs)

        self.category = self.data.get('category')

        self.type = None
        self.value = None

        for filter_type in self.filter_types:
            if filter_type in self.data:
                self.type = filter_type
                self.value = self.data.get(filter_type)
                break

    def process_me(self, processor):
        processor.process_unspecified(self)




# ALOHA: 
# Android: 
# Search_Filter_Apply [ 
# category=hotel 
# ]
# iOS:
# Search_Filter_Apply [ 
# Country=CA 
# Language=en-CA 
# Orientation=Portrait 
# category=hotel 
# ]


class SearchFilterApply(DictEvent):
    keys = (
        'Search_Filter_Apply', 
    )

    def __init__(self, *args, **kwargs):
        super(SearchFilterApply, self).__init__(*args, **kwargs)

        self.category = self.data.get('category')

    def process_me(self, processor):
        processor.process_unspecified(self)

