import datetime
import ctypes
import itertools


ctypes.set_conversion_mode('utf8', 'strict')


class C_EVENT_TIME(ctypes.Structure):
	_fields_ = [
		('client_created', ctypes.c_uint64),
		('server_upload', ctypes.c_uint64)
	]

	dtime = None
	accuracy = 0

	def _setup_time(self):
		self.client_dtime = datetime.datetime.utcfromtimestamp(
			self.client_created / 1000.  # timestamp is in millisecs
		)
		self.server_dtime = datetime.datetime.utcfromtimestamp(
			self.server_upload / 1000.  # timestamp is in millisecs
		)
		self.dtime = self.client_dtime
		self.accuracy = 0

	def get_approx_time(self):
		if self.dtime is None:
			self._setup_time()
		return self.dtime, self.accuracy


class C_USER_INFO(ctypes.Structure):
	_fields_ = [
		('latitude', ctypes.c_float),
		('longitude', ctypes.c_float),
		('has_geo', ctypes.c_bool),
		('uid', ctypes.c_char_p)
	]

	def get_location(self):
		if self.has_geo:
			return (self.latitude, self.longitude)
		return None


C_CALLBACK = ctypes.CFUNCTYPE(
	None,
	ctypes.c_char_p,
	ctypes.POINTER(C_EVENT_TIME),
	ctypes.POINTER(C_USER_INFO),
	ctypes.POINTER(ctypes.c_char_p),
	ctypes.c_int
)  # key, event_time, user_info, data, data_len


def iterate_events(stream_processor):
	C_ITERATOR_MODULE = ctypes.cdll.LoadLibrary("../api/iterate_events.so")
	use_keys = tuple(itertools.chain.from_iterable(
		e.keys for e in stream_processor.__events__
	))
	KEY_LIST = ctypes.c_char_p * len(use_keys)
	C_ITERATOR_MODULE.iterate.argtypes = [C_CALLBACK, KEY_LIST, ctypes.c_int]
	C_ITERATOR_MODULE.iterate(
		C_CALLBACK(
			stream_processor.process_event
		),
		KEY_LIST(*use_keys),
		len(use_keys)
	)
