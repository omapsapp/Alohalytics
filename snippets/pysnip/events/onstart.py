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

    __slots__ = tuple()

    @property
    def connection(self):
        try:
            if self.data['connected'] == 'yes':
                # wifi or not
                return self.data.get('ctype') or 'mobile'
        except KeyError:
            pass

        return None

    @property
    def in_roaming(self):
        try:
            if self.data['connected'] == 'yes':
                return self.data.get('roaming', 'no') == 'yes'
        except KeyError:
            pass

        return None

    def __dumpdict__(self):
        d = super(TechnicalLaunch, self).__basic_dumpdict__()
        d.update({
            'connection': self.connection(),
            'in_roaming': self.in_roaming()
        })
        return d


# TechnicalLaunch event in iOS is always associated with a UI launch

class IOSVisibleLaunch(TechnicalLaunch):
    __slots__ = tuple()


# This event is trusted to be the one associated with an actual UI launch
# in Android

class AndroidVisibleLaunch(Event):
    keys = (
        '$onResume',
    )

    __slots__ = tuple()

# SESSIONS


class AndroidSessionStart(Event):
    keys = (
        '$startSession',
    )

    __slots__ = tuple()


class AndroidSessionEnd(Event):
    keys = (
        '$endSession',
    )

    __slots__ = tuple()


class IOSSessionStart(Event):
    keys = (
        '$applicationDidBecomeActive',
    )

    __slots__ = tuple()


class IOSSessionEnd(Event):
    keys = (
        '$applicationDidEnterBackground',
        # 'Framework::EnterBackground',
    )

    __slots__ = tuple()
