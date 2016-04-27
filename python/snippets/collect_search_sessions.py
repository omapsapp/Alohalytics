import collections
import datetime
import codecs
import os
import shutil
import multiprocessing

from alohalytics import StreamProcessor as BaseProcessor
from alohalytics import ResultCollector as BaseResultCollector

import events


class SearchSession(dict):
	def __init__(self, start, location=None):
		self[u'start'] = start
		self[u'location'] = location
		self[u'end'] = None
		self[u'queries'] = []


class StreamProcessor(BaseProcessor):
	__events__ = (events.SearchResults, events.GPSTracking)

	def __init__(self):
		self.count_events = 0

		self._suggest_sessions = collections.defaultdict(list)
		self.locations = {}
		self._inactive_threshold = datetime.timedelta(minutes=5)

		self.search_sessions = collections.defaultdict(list)

	def process_gps_tracking(self, event):
		loc = event.user_info.get_location()
		if not loc:
			return

		uid = event.user_info.uid
		self.locations[uid] = loc

		if uid in self.search_sessions:
			for session in reversed(self.search_sessions[uid]):
				if session[u'location'] is not None:
					break
				session[u'location'] = loc


	# DO NOT write to stdin or stderr
	def process_search_results(self, event):
		# init new search session
		uid = event.user_info.uid
		user_sessions = self.search_sessions[uid]
		suggest_history = self._suggest_sessions[uid]
		try:
			current_session = user_sessions[-1]
			inactive_interval = event.event_time.dtime - current_session[u'end']
			if inactive_interval > self._inactive_threshold:
				raise IndexError()
		except IndexError:
			current_session = SearchSession(
				start=event.event_time.dtime,
				location=self.locations.get(uid, None)
			)
			user_sessions.append(current_session)
			suggest_history = self._suggest_sessions[uid] = []

		current_session[u'end'] = event.event_time.dtime

		if suggest_history and\
				event.query not in suggest_history[-1] and\
				suggest_history[-1] not in event.query:
			current_session[u'queries'].append(suggest_history[-1])
			suggest_history = self._suggest_sessions[uid] = []

		suggest_history.append(event.query)

		self.count_events += 1

	def finish(self):
		for uid, suggest_history in self._suggest_sessions.iteritems():
			self.search_sessions[uid][-1][u'queries'].append(suggest_history[-1])

		logger = multiprocessing.get_logger()
		logger.info('Done: %s' % (self.count_events,))

		del self._suggest_sessions
		del self.locations


class ResultCollector(BaseResultCollector):
	def __init__(self):
		super(ResultCollector, self).__init__()
		self.total_count = 0

		self.results_dir = os.path.join('/home/a.vodolazskiy', 'stats', 'requests')
		self.created_dirs = set()
		shutil.rmtree(self.results_dir, ignore_errors=True)

	def get_result_file_path(self, session):
		start_dtime = eval(session['start'])
		year_dir = os.path.join(self.results_dir, str(start_dtime.year))
		if start_dtime.year not in self.created_dirs:
			try:
				os.makedirs(year_dir)
				self.created_dirs.add(start_dtime.year)
			except OSError:
				pass
		return os.path.join(year_dir, str(start_dtime.month))

	def add(self, processor_results):
		self.total_count += processor_results.count_events

		for uid, sessions in processor_results.search_sessions.iteritems():
			for s in sessions:
				for q in s['queries']:
					fname = self.get_result_file_path(s)
					with codecs.open(fname, 'a+', 'utf8') as fout:
						fout.write('%s\t%s\t%s\t%s\t%s\n' % (
							uid,
							eval(s['start']).strftime('%Y%m%d_%H:%M:%S'),
							eval(s['end']).strftime('%Y%m%d_%H:%M:%S'),
							repr(s['location']),
							q.replace('\t', ' ')
						))
		logger = multiprocessing.get_logger()
		logger.info('Dumped: %s' % (self.total_count,))

	def get_stats(self):
		return self.total_count
