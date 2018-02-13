# -*- coding: utf-8 -*-

from pyaloha.event import Event, DictEvent


# ALOHA: 
# Editor_Add_start [ 
# is_authenticated=false 
# is_online=true 
# mwm_name=INVALID 
# mwm_version=-1.0 
# ]
# Editor_Add_success [ 
# is_authenticated=false 
# is_online=false 
# mwm_name=Iran_North 
# mwm_version=170119.0 
# ]
# 

class EditorAdd(DictEvent):
    keys = (
        'Editor_Add_start', 'Editor_Add_success'
    )

    def __init__(self, *args, **kwargs):
        super(EditorAdd, self).__init__(*args, **kwargs)

        try:
            self.auth = bool(self.data['is_authenticated'])
        except KeyError:
            self.auth = None

        try:
            self.online = bool(self.data['is_online'])
        except KeyError:
            self.online = None

        try:
            self.mwm_name = self.data['mwm_name']
        except KeyError:
            self.mwm_name = None

        try:
            self.mwm_version = self.data['mwm_version']
        except KeyError:
            self.mwm_version = None

        if self.key == 'Editor_Add_start':
            self.action = 'start'
        elif self.key == 'Editor_Add_success':
            self.action = 'finish'

        self.mode = 'add'

    def process_me(self, processor):
        processor.process_unspecified(self)

# ALOHA: 
# Editor_Add_click [ 
# from=main_menu 
# ]

class EditorAddClick(DictEvent):
    keys = (
        'Editor_Add_click',
    )

    def __init__(self, *args, **kwargs):
        super(EditorAddClick, self).__init__(*args, **kwargs)

        try:
            self.source = self.data['from']
        except KeyError:
            self.source = None

    def process_me(self, processor):
        processor.process_unspecified(self)

# ALOHA: 
# Editor_Edit_start [ 
# is_authenticated=false 
# is_online=false 
# mwm_name=Nepal_Kathmandu 
# mwm_version=171020.0 
# ]
# Editor_Edit_success [ 
# is_authenticated=false 
# is_online=false 
# mwm_name=Nepal_Kathmandu 
# mwm_version=171020.0 
# ]

class EditorEdit(DictEvent):
    keys = (
        'Editor_Edit_start', 'Editor_Edit_success'
    )

    def __init__(self, *args, **kwargs):
        super(EditorEdit, self).__init__(*args, **kwargs)

        try:
            self.auth = bool(self.data['is_authenticated'])
        except KeyError:
            self.auth = None

        try:
            self.online = bool(self.data['is_online'])
        except KeyError:
            self.online = None

        try:
            self.mwm_name = self.data['mwm_name']
        except KeyError:
            self.mwm_name = None

        try:
            self.mwm_version = self.data['mwm_version']
        except KeyError:
            self.mwm_version = None

        if self.key == 'Editor_Edit_start':
            self.action = 'start'
        elif self.key == 'Editor_Edit_success':
            self.action = 'finish'

        self.mode = 'edit'

    def process_me(self, processor):
        processor.process_unspecified(self)



# ALOHA: 
# UGC_Review_start [ 
# from=placepage 
# is_authenticated=false 
# is_online=true 
# mode=add 
# ]

class UGCReviewStart(DictEvent):
    keys = (
        'UGC_Review_start',
    )

    def __init__(self, *args, **kwargs):
        super(UGCReviewStart, self).__init__(*args, **kwargs)

        try:        
            self.auth = self.to_bool(self.data['is_authenticated'])
        except KeyError:
            self.auth = None
        
        try:
            self.online = self.to_bool(self.data['is_online'])
        except KeyError:    
            self.online = None

        try:
            self.source = self.data['from']
        except KeyError:
            self.source = None

        try:
            self.mode = self.data['mode']
        except KeyError:
            self.mode = None

    def to_bool(seld, s):
        return {'1': True,'true': True,'0': False,'false': False}.get(s)

    def process_me(self, processor):
        processor.process_unspecified(self)

# ALOHA: 
# UGC_Review_success [ 
# ]

class UGCReviewSuccess(DictEvent):
    keys = (
        'UGC_Review_success',
    )

    def __init__(self, *args, **kwargs):
        super(UGCReviewSuccess, self).__init__(*args, **kwargs)

    def process_me(self, processor):
        processor.process_unspecified(self)

# ALOHA: 
# UGC_Auth_error [ 
# error=CONNECTION_FAILURE: CONNECTION_FAILURE 
# provider=facebook 
# ]
# UGC_Auth_error [ 
# Country=NL 
# Error=The user canceled the sign-in flow. 
# Language=nl-NL 
# Orientation=Portrait 
# Provider=Google 
# ]

class UGCAuthError(DictEvent):
    keys = (
        'UGC_Auth_error', 
    )

    def __init__(self, *args, **kwargs):
        super(UGCAuthError, self).__init__(*args, **kwargs)

    def process_me(self, processor):
        processor.process_unspecified(self)
# ALOHA: 
# UGC_Auth_external_request_success [ 
# Country=CZ 
# Language=cs-CZ 
# Orientation=Landscape 
# Provider=Google 
# ]
# UGC_Auth_external_request_success [ 
# provider=facebook 
# ]

class UGCAuthSuccess(DictEvent):
    keys = (
        'UGC_Auth_external_request_success', 
    )

    def __init__(self, *args, **kwargs):
        super(UGCAuthSuccess, self).__init__(*args, **kwargs)

    def process_me(self, processor):
        processor.process_unspecified(self)

# 'UGC_Auth_shown', 'UGC_Auth_declined'
