# -*- coding: utf-8 -*-

from pyaloha.event import DictEvent

# Events *_start send, when user open editor for add/edit point.
# Events *_success send, when user successfully finish edit point.
#
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


class EditorStart(DictEvent):
    keys = (
        'Editor_Add_start', 'Editor_Add_success',
        'Editor_Edit_start', 'Editor_Edit_success'
    )

    def __init__(self, *args, **kwargs):
        super(EditorStart, self).__init__(*args, **kwargs)

        self.auth = self.to_bool(self.data.get('is_authenticated'))
        self.online = self.to_bool(self.data.get('is_online'))

        self.mwm_name = self.data.get('mwm_name')
        self.mwm_version = self.data.get('mwm_version')

        if self.key == 'Editor_Add_start':
            self.action = 'start'
            self.mode = 'add'
        elif self.key == 'Editor_Add_success':
            self.action = 'finish'
            self.mode = 'add'
        elif self.key == 'Editor_Edit_start':
            self.action = 'start'
            self.mode = 'edit'
        elif self.key == 'Editor_Edit_success':
            self.action = 'finish'
            self.mode = 'edit'

        del self.data

    def to_bool(self, s):
        return {'1': True, 'true': True, '0': False, 'false': False, 'Yes': True, 'No': False}.get(s)



# Event send, when user click «Add place (business)» and start choose
# position of company.
# When user tap «Done» — send event 'Editor_Add_start'
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

        self.source = self.data.get('from')


# Event send, when user start write a review
# ALOHA:
# UGC_Review_start [
# from=placepage
# is_authenticated=false
# is_online=true
# mode=add
# ]
# from = {'placepage', 'placepage_preview'}
# mode = {'add'}


class UGCReviewStart(DictEvent):
    keys = (
        'UGC_Review_start',
    )

    def __init__(self, *args, **kwargs):
        super(UGCReviewStart, self).__init__(*args, **kwargs)

        self.auth = self.to_bool(self.data.get('is_authenticated'))
        self.online = self.to_bool(self.data.get('is_online'))
        self.source = self.data.get('from')
        self.mode = self.data.get('mode')

    def to_bool(self, s):
        return {'1': True, 'true': True, '0': False, 'false': False}.get(s)


# Event send, when user successfully finish write a review
# ALOHA:
# UGC_Review_success [
# ]


class UGCReviewSuccess(DictEvent):
    keys = (
        'UGC_Review_success',
    )


# Event send, when something went wrong with authentication.
#
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


# Event send, when authentication after write review was successful
#
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


# TODO:
# 'UGC_Auth_shown', 'UGC_Auth_declined'
