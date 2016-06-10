from pyaloha.event import Event, DictEvent


# Event of the app launch with props:
# connection: None, wifi, mobile
# in_roaming: True, False
# user_info.get_location(): None, (lat, lon)
# user_info.uid
# user_info.os_t: 0 (Unknown), 1 (Android), 2 (iOS)

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


class IOSVisibleLaunch(TechnicalLaunch):
    pass


class AndroidVisibleLaunch(Event):
    keys = (
        '$onResume',
    )
