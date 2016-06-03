"""
    This module defines base classes for worker, aggregator and stats
processor.
    Look at pyaloha.main module for a pipeline sequence understanding.
"""

from __future__ import print_function

import multiprocessing
import shutil
import traceback

from pyaloha.event_factory import EventFactory
from pyaloha.protocol import WorkerResults


class DataStreamWorker(object):
    """
    This is a base class representing one of the workers
that preprocess given raw events (one by one).
    This worker is not guaranteed to have all available data, so do not try
to write a stats processor class. This is a low-level preprocessor/filter/etc.
    @method process_unspecified is a generic method called on every event
despite of its actual type in its own process. In general this is
the most basic method to overload while writing worker in your script.
    __events__ field is used in low-level filtering of the events to provide to
specific worker.
    """

    __events__ = tuple()

    def __init__(self, event_factory=None):
        self._event_factory = event_factory or EventFactory(custom_events=[])

    def process_unspecified(self, event):
        pass

    def process_event(self,
                      key, event_time_p, user_info_p,
                      str_data_p, str_data_len):
        """
        Main callback used in the main event stream processing loop
        """
        try:
            ev = self._event_factory.make_event(
                key, event_time_p[0], user_info_p[0],
                str_data_p, str_data_len
            )
            ev.process_me(self)
        except Exception:
            logger = multiprocessing.get_logger()
            logger.error(traceback.format_exc())

    def dumps_results(self):
        return WorkerResults.dumps_object(self, debug=False)

    def pre_output(self):
        pass


class DataAggregator(object):
    """
    This is a 'singletone' class that accumulates results from the workers.
    @method aggregate must be overloaded in your script.
It is called every time a worker is done with its events to accumulate results.
    @method post_aggregate is an optional method.
It is called after all results are accumulated.
Look for an example in daily_over_fs usage pattern.
    """

    def __init__(self, results_dir=None, post_aggregate_worker=lambda x: x):
        self.post_aggregate_worker = post_aggregate_worker

        self.results_dir = results_dir
        if self.results_dir:
            self.created_dirs = set()
            shutil.rmtree(self.results_dir, ignore_errors=True)

    def aggregate(self):
        raise NotImplementedError()

    def post_aggregate(self, pool=None):
        pass


class StatsProcessor(object):
    """
    This is fully prepared stats data processor and printer. It is instantiated
with a pointer to aggregator that has already been done with all workers and
his own postprocessing.
    Class can be used as a business logic processor
(it is guaranteed to have all available data) or just as a sequencial printer
(if actual stats processing logic is simple).
    @method gen_stats must be overloaded in your script.
It is called at the end of the stats processing pipeline and
yields one or several stats sections - each with a human-readable text header
and a sequence of sequence objects interpreted as a table of values.
    @method process_stats is optional.
It is called just before calling gen_stats.
    """
    def __init__(self, aggregator):
        self.aggregator = aggregator

    def process_stats(self):
        pass

    def gen_stats(self):
        """
        Look at @method print_stats for a results format to be generated
        """
        raise NotImplementedError()

    def print_stats(self):
        for header, stats_generator in self.gen_stats():
            print('-' * 20)
            print(header)
            print('-' * 20)
            for row in stats_generator:
                print(u'\t'.join(map(unicode, row)))
            print()
