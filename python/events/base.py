import ctypes


def c_unicode(c_data):
    return unicode(ctypes.string_at(c_data), 'utf8')


def c_string(c_data):
    return c_data


class Event(object):
    def __init__(self,
                 key, event_time, user_info,
                 data_list, data_list_len):
        self.data_list = data_list
        self.data_list_len = data_list_len
        event_time._setup_time()
        self.event_time = event_time
        self.user_info = user_info
        self.user_info.setup()
        self.key = key

    def process_me(self, processor):
        processor.process_unspecified(self)


class _PairsEvent(Event):
    def __init__(self,
                 key, event_time, user_info,
                 data_list, data_list_len):
        super(_PairsEvent, self).__init__(
            key, event_time, user_info,
            data_list, data_list_len
        )

        self.data = dict(
            (self.data_list[i], self.data_list[i + 1])
            for i in range(0, data_list_len, +2)
        )
