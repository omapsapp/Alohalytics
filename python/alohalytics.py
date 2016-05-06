#!/bin/env python2.7

import datetime
import inspect
import json
import multiprocessing
import os
import sys
import traceback

from events.factory import make_event

from worker import invoke_cmd_worker, load_plugin, setup_logs


DAY_FORMAT = '%Y%m%d'


def day_serialize(dtime):
    return dtime.strftime(DAY_FORMAT)


def day_deserialize(s):
    return datetime.datetime.strptime(s, DAY_FORMAT)


def str2date(s):
    return day_deserialize(s).date()


def custom_loads(dct):
    if '__stype__' in dct and dct['__stype__'] == 'repr':
        return eval(dct['__svalue__'])
    return dct


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, set, frozenset)):
            return {'__stype__': 'repr', '__svalue__': repr(obj)}
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


class ProcessorResults(object):
    @classmethod
    def dumps_object(cls, obj, debug=False):
        '''
        NOTE: Please, check the keys of your dicts to be basic types only
        '''
        return json.dumps(
            [
                pair
                for pair in inspect.getmembers(
                    obj, lambda m: not callable(m)
                )
                if not pair[0].startswith('_')
            ],
            cls=CustomEncoder
        )

    @classmethod
    def loads(cls, json_text):
        instance = ProcessorResults()
        for key, value in json.loads(json_text, object_hook=custom_loads):
            setattr(instance, key, value)
        return instance


class StreamProcessor(object):
    __events__ = tuple()

    def process_search_results(self, event):
        pass

    def process_gps_tracking(self, event):
        pass

    def process_routing(self, event):
        pass

    def process_unspecified(self, event):
        pass

    def process_event(self,
                      key, event_time_p, user_info_p,
                      str_data_p, str_data_len):
        try:
            ev = make_event(
                key, event_time_p[0], user_info_p[0],
                str_data_p, str_data_len
            )
            ev.process_me(self)
        except Exception:
            logger = multiprocessing.get_logger()
            logger.error(traceback.format_exc())

    def dumps_results(self):
        return ProcessorResults.dumps_object(self, debug=False)


class ResultCollector(object):
    def __init__(self, results_dir=None):
        self.results_dir = results_dir
        if self.results_dir:
            self.created_dirs = set()
            shutil.rmtree(self.results_dir, ignore_errors=True)

    def get_result_file_path(self, dte):
        if not self.results_dir:
            raise Exception('Results dir is not set to use this method')

        year_dir = os.path.join(self.results_dir, str(dte.year))
        if dte.year not in self.created_dirs:
            try:
                os.makedirs(year_dir)
                self.created_dirs.add(dte.year)
            except OSError:
                pass
        return os.path.join(year_dir, str(dte.month))

    def add(self, processor_results):
        raise NotImplementedError()

    # look at print_stats for results format
    def get_stats(self):
        raise NotImplementedError()

    def print_stats(self):
        for header, stats in self.gen_stats():
            print '-' * 20
            print header
            print '-' * 20
            for row in stats:
                print '\t'.join(map(unicode, row))
            print


def process_all(data_dir, plugin,
                start_date=None, end_date=None,
                worker_num=3 * multiprocessing.cpu_count() / 4):
    setup_logs()
    try:
        pool = multiprocessing.Pool(worker_num)

        items = (
            (plugin, os.path.join(data_dir, fname))
            for fname in os.listdir(data_dir)
            if check_fname(fname, start_date, end_date)
        )

        collector = load_plugin(plugin).ResultCollector()
        for results in pool.imap_unordered(invoke_cmd_worker, items):
            collector.add(ProcessorResults.loads(results))
    finally:
        pool.terminate()
        pool.join()

    return collector


def run(plugin_name, start_date, end_date,
        data_dir='/mnt/disk1/alohalytics/by_date'):
    collector = process_all(
        data_dir, plugin_name,
        start_date, end_date
    )
    collector.print_stats()


def check_fname(filename, start_date, end_date):
    if filename[0] == '.':
        return False
    return check_date(filename, start_date, end_date)


def check_date(filename, start_date, end_date):
    fdate = str2date(filename[-11:-3])
    if start_date and fdate < start_date:
        return False
    if end_date and fdate > end_date:
        return False
    return True


if __name__ == '__main__':
    plugin_name = sys.argv[1]
    try:
        start_date, end_date = map(str2date, sys.argv[2:4])
    except ValueError:
        start_date, end_date = None, None

    run(plugin_name, start_date, end_date)
