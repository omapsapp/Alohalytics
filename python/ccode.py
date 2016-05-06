import ctypes
import datetime
import itertools


ctypes.set_conversion_mode('utf8', 'strict')


class CEVENTTIME(ctypes.Structure):
    _fields_ = [
        ('client_created', ctypes.c_uint64),
        ('server_upload', ctypes.c_uint64)
    ]

    dtime = None
    is_accurate = False

    current_time = datetime.datetime.utcnow()

    def _setup_time(self):
        self.client_dtime = datetime.datetime.utcfromtimestamp(
            self.client_created / 1000.  # timestamp is in millisecs
        )
        self.server_dtime = datetime.datetime.utcfromtimestamp(
            self.server_upload / 1000.  # timestamp is in millisecs
        )

        self.dtime = self.server_dtime
        if self.client_dtime.year >= self.current_time.year - 1 and\
                self.client_dtime <= self.current_time:
            self.dtime = self.client_dtime

            self.is_accurate = True

    def get_approx_time(self):
        if self.dtime is None:
            self._setup_time()
        return self.dtime, self.accuracy


class CUSERINFO(ctypes.Structure):
    _fields_ = [
        ('latitude', ctypes.c_float),
        ('longitude', ctypes.c_float),
        ('has_geo', ctypes.c_bool),
        ('os_type', ctypes.c_char),
        ('uid', ctypes.c_char_p)
    ]

    def __init__(self, *args, **kwargs):
        super(CUSERINFO, self).__init__(*args, **kwargs)
        self.uid = int(self.uid, 16)

    def get_location(self):
        if self.has_geo:
            return (self.latitude, self.longitude)
        return None


CCALLBACK = ctypes.CFUNCTYPE(
    None,
    ctypes.c_char_p,
    ctypes.POINTER(CEVENTTIME),
    ctypes.POINTER(CUSERINFO),
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.c_int
)  # key, event_time, user_info, data, data_len


def iterate_events(stream_processor):
    c_module = ctypes.cdll.LoadLibrary("../api/build/iterate_events.so")
    use_keys = tuple(itertools.chain.from_iterable(
        e.keys for e in stream_processor.__events__
    ))
    keylist_type = ctypes.c_char_p * len(use_keys)
    c_module.iterate.argtypes = [CCALLBACK, keylist_type, ctypes.c_int]
    c_module.iterate(
        CCALLBACK(
            stream_processor.process_event
        ),
        keylist_type(*use_keys),
        len(use_keys)
    )
