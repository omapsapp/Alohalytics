import ctypes
import datetime
import itertools
import os
import sys

from pyaloha.protocol import SerializableDatetime

try:
    from ctypes import set_conversion_mode
except ImportError:
    pass
else:
    set_conversion_mode('utf8', 'strict')


def c_unicode(c_data):
    return unicode(ctypes.string_at(c_data), 'utf8')


def c_string(c_data):
    return c_data


class CEVENTTIME(ctypes.Structure):
    _fields_ = [
        ('client_creation', ctypes.c_uint64),
        ('server_upload', ctypes.c_uint64)
    ]

    delta_past = datetime.timedelta(days=6 * 30)
    delta_future = datetime.timedelta(days=1)

    def get_approx_time(self):
        if not self.dtime:
            self._setup_time()
        return self.dtime, self.is_accurate

    def make_object(self):
        client_dtime = SerializableDatetime.utcfromtimestamp(
            self.client_creation / 1000.  # timestamp is in millisecs
        )
        server_dtime = SerializableDatetime.utcfromtimestamp(
            self.server_upload / 1000.  # timestamp is in millisecs
        )

        dtime = server_dtime
        if client_dtime >= server_dtime - CEVENTTIME.delta_past and\
                client_dtime <= server_dtime + CEVENTTIME.delta_future:
            dtime = client_dtime

        pytime = PythonEventTime()
        pytime.client_creation = client_dtime
        pytime.server_upload = server_dtime
        pytime.dtime = dtime
        return pytime


class PythonEventTime(object):
    __slots__ = (
        'client_creation', 'server_upload',
        'dtime', 'is_accurate'
    )

    @property
    def is_accurate(self):
        return self.dtime == self.client_creation

    def __dumpdict__(self):
        return {
            'dtime': self.dtime,
            'is_accurate': self.is_accurate
        }


class IDInfo(ctypes.Structure):
    _fields_ = [
        ('os', ctypes.c_byte),
    ]

    _os_valid_range = range(3)

    __slots__ = ('os', 'uid')

    def validate(self):
        if self.os not in IDInfo._os_valid_range:
            raise ValueError('Incorrect os value: %s' % self.os)


class GeoIDInfo(IDInfo):
    _fields_ = [
        ('lat', ctypes.c_float),
        ('lon', ctypes.c_float)
    ]

    __slots__ = ('lat', 'lon')

    def has_geo(self):
        # TODO: if client will send actual (0, 0) we will
        # intepretate them as a geo info absence.
        # For now it is acceptable though.
        return (
            round(self.lat, 2) != 0.0 or
            round(self.lon, 2) != 0.0
        )

    def get_location(self):
        if self.has_geo():
            return (self.lat, self.lon)
        return None


class CUSERINFO(GeoIDInfo):
    _fields_ = [
        ('raw_uid', (ctypes.c_char * 32)),
    ]

    __slots__ = ('raw_uid',)

    def make_object(self):
        self.validate()

        if self.has_geo():
            pyinfo = PythonGeoUserInfo()
            pyinfo.uid = int(self.raw_uid, 16)
            pyinfo.os = self.os
            pyinfo.lat = round(self.lat, 6)
            pyinfo.lon = round(self.lon, 6)
            return pyinfo

        pyinfo = PythonUserInfo()
        pyinfo.uid = int(self.raw_uid, 16)
        pyinfo.os = self.os
        return pyinfo


class PythonUserInfo(object):
    __slots__ = ('uid', 'os')

    @property
    def has_geo(self):
        return False

    def is_on_android(self):
        return self.os == 1

    def is_on_ios(self):
        return self.os == 2

    def is_on_unknown_os(self):
        return self.os == 0

    def __dumpdict__(self):
        return {
            'os': self.os,
            'uid': self.uid
        }


class PythonGeoUserInfo(PythonUserInfo):
    __slots__ = ('lat', 'lon')

    @property
    def has_geo(self):
        return True

    def __dumpdict__(self):
        d = super(PythonGeoUserInfo, self).__dumpdict__()
        d.update({
            'lat': self.lat,
            'lon': self.lon
        })
        return d


CCALLBACK = ctypes.CFUNCTYPE(
    None,
    ctypes.c_char_p,
    ctypes.POINTER(CEVENTTIME),
    ctypes.POINTER(CUSERINFO),
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.c_int
)  # key, event_time, user_info, data, data_len


def iterate_events(stream_processor, events_limit):
    base_path = os.path.dirname(os.path.abspath(__file__))
    c_module = ctypes.cdll.LoadLibrary(
        os.path.join(base_path, 'iterate_events.so')
    )
    use_keys = tuple(itertools.chain.from_iterable(
        e.keys for e in stream_processor.__events__
    ))
    keylist_type = ctypes.c_char_p * len(use_keys)
    c_module.Iterate.argtypes = [CCALLBACK, keylist_type, ctypes.c_int]
    c_module.Iterate(
        CCALLBACK(
            stream_processor.process_event
        ),
        keylist_type(*use_keys),
        len(use_keys),
        events_limit
    )
