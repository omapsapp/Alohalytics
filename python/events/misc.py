from .base import Event, c_string, c_unicode

class SearchResults(Event):
	keys = ('searchEmitResults',)

	def __init__(self, *args, **kwargs):
		super(SearchResults, self).__init__(*args, **kwargs)

		self.query = c_unicode(self.data_list[0])
		self.result_num = int(c_string(self.data_list[1]) or 0)

		self.data_list = None

	def process_me(self, processor):
		processor.process_search_results(self)


class GPSTracking(Event):
	keys = (
		'Flurry:logLocation', '$launch', 'Framework:EnterBackground'
	)

	def __init__(self, *args, **kwargs):
		super(GPSTracking, self).__init__(*args, **kwargs)

		self.data_list = None

	def process_me(self, processor):
		processor.process_gps_tracking(self)
