class Event(object):
    def __init__(self,
                 key, event_time, user_info,
                 data_list=None, data_list_len=0):
        if data_list_len:
            self.data_list = data_list
            self.data_list_len = data_list_len
        event_time._setup_time()
        self.event_time = event_time
        self.user_info = user_info
        self.user_info.setup()
        self.key = key

    def process_me(self, processor):
        processor.process_unspecified(self)

    def __basic_dumpdict__(self):
        return self.__dumpdict__()

    def __dumpdict__(self):
        return {
            'key': self.key,
            'type': self.__class__.__name__,
            'user_info': self.user_info.stripped(),
            'event_time': self.event_time
        }


class DictEvent(Event):
    """
    This is a simplified form of any Alohalytics pairs event
when all event params (except datetime and user/device identification)
are accumulated into a dict.
    You can try to convert Event instance to it with a @method from_event.
    """
    __slots__ = ('data', 'event_time', 'key', 'user_info')

    def __init__(self,
                 key, event_time, user_info,
                 data_list, data_list_len):
        super(DictEvent, self).__init__(
            key, event_time, user_info
        )

        if data_list_len % 2 != 0:
            raise ValueError(
                "Event can't be casted to a dict without additional knowledge"
            )

        self.data = {
            data_list[i]: data_list[i + 1]
            for i in range(0, data_list_len, +2)
        }

    @classmethod
    def from_event(cls, event):
        return DictEvent(
            event.key,
            event.event_time, event.user_info,
            event.data_list, event.data_list_len
        )

    def __basic_dumpdict__(self):
        return super(DictEvent, self).__dumpdict__()

    def __dumpdict__(self):
        d = self.__basic_dumpdict__()
        d.update(self.data)
        return d
