import collections
import datetime
import codecs
import os
import shutil
import multiprocessing

from alohalytics import StreamProcessor as BaseProcessor
from alohalytics import ResultCollector as BaseResultCollector
from alohalytics import day_serialize, day_deserialize

import events


class StreamProcessor(BaseProcessor):
	__events__ = (events.onstart.Launch,)

	def __init__(self):
		self.visit_days = collections.defaultdict(set)
		self.count_events = 0

	def process_unspecified(self, event):
		self.count_events += 1
		uid = event.user_info.uid
		dtime = event.event_time.dtime
		self.visit_days[day_serialize(dtime)].add(uid)

	def finish(self):
		pass


class ResultCollector(BaseResultCollector):
	def __init__(self):
		super(ResultCollector, self).__init__()
		self.total_count = 0
		self.agg_visit_days = collections.defaultdict(set)

		self.results_dir = os.path.join('/home/a.vodolazskiy', 'stats', 'users')
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

		for dte, uids in processor_results.visit_days.iteritems():
			self.agg_visit_days[day_deserialize(dte)].update(uids)

	def get_stats(self):
		days_num = collections.Counter()
		months = collections.defaultdict(set)
		for dte, uids in sorted(self.agg_visit_days.iteritems()):
			yield dte, len(uids)
			for u in uids:
				days_num[u] += 1
			months[(dte.year, dte.month)].update(uids)

		rev_days_num = collections.Counter()
		for u, cnt in days_num.iteritems():
			rev_days_num[cnt] += 1
		for dnum, cnt in rev_days_num.most_common(100):
			yield dnum, cnt

		months = sorted(months.iteritems())
		for m_count in range(3, len(months), +1):
			yield months[m_count][0], len(
				months[m_count][1]
				.intersection(months[m_count - 1][1])
				.intersection(months[m_count - 2][1])
			)

