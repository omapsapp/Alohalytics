from .base import _PairsEvent

# Event of the app launch with props:
# connection: None, wifi, mobile
# in_roaming: True, False
# user_info.get_location(): None, (lat, lon)


class Launch(_PairsEvent):
    keys = (
        '$launch',
    )

    def __init__(self, *args, **kwargs):
        super(Launch, self).__init__(*args, **kwargs)

        try:
            if self.data['connected'] == 'yes':
                # wifi or not
                self.connection = self.data.get('ctype') or 'mobile'
                self.in_roaming = self.data.get('roaming', 'no') == 'yes'
        except KeyError:
            self.connection = None
            self.in_roaming = None
