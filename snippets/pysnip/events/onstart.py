from pyaloha.event import Event, DictEvent


# App launch event. It is not necessary visible for a user.
# Its properties are:
# connection: {None, wifi, mobile}
# in_roaming: {True, False}
# user_info.get_location(): None or (lat, lon)
# user_info.uid
# user_info.os: {0 (Unknown), 1 (Android), 2 (iOS)}

class TechnicalLaunch(DictEvent):
    keys = (
        '$launch',
    )

    def __init__(self, *args, **kwargs):
        super(TechnicalLaunch, self).__init__(*args, **kwargs)

        try:
            if self.data['connected'] == 'yes':
                # wifi or not
                self.connection = self.data.get('ctype') or 'mobile'
                self.in_roaming = self.data.get('roaming', 'no') == 'yes'
        except KeyError:
            self.connection = None
            self.in_roaming = None


# TechnicalLaunch event in iOS is always associated with a UI launch

class IOSVisibleLaunch(TechnicalLaunch):
    pass


# This event is trusted to be the one associated with an actual UI launch
# in Android

class AndroidVisibleLaunch(Event):
    keys = (
        '$onResume',
    )
