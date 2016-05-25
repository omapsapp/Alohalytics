#!/bin/env python2.7

import datetime
import inspect
import itertools
import json
import multiprocessing
import os
import shutil
import sys
import traceback

from events.factory import make_event

from worker import invoke_cmd_worker, load_plugin, setup_logs


DAY_FORMAT = '%Y%m%d'
UNIQ_DAY_FORMAT = 'dt' + DAY_FORMAT


def day_serialize(dtime):
    return dtime.strftime(UNIQ_DAY_FORMAT)


def day_deserialize(s):
    return datetime.datetime.strptime(s, UNIQ_DAY_FORMAT)


def str2date(s):
    return datetime.datetime.strptime(s, DAY_FORMAT).date()


def custom_loads(dct):
    # if '__loaddict__' in dct:
    #    try:
    #        eval(dct['__preload__'])
    #    except KeyError:
    #        pass
    #    return eval(dct['__loaddict__'])(dct)

    if '__stype__' in dct and dct['__stype__'] == 'repr':
        return eval(dct['__svalue__'])

    for str_key in dct.keys():
        try:
            int_key = int(str_key)
        except ValueError:
            break
        else:
            dct[int_key] = dct[str_key]
            del dct[str_key]

    return dct


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dumpdict__'):
            return obj.__dumpdict__()

        if isinstance(obj, (datetime.datetime, datetime.date, set, frozenset)):
            return {'__stype__': 'repr', '__svalue__': repr(obj)}
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


class FileProtocol(object):
    @classmethod
    def dumps(cls, obj, debug=False):
        return json.dumps(
            obj, cls=CustomEncoder
        )

    @classmethod
    def loads(cls, json_text):
        return json.loads(json_text, object_hook=custom_loads)


class ProcessorResults(FileProtocol):
    @classmethod
    def dumps_object(cls, obj, debug=False):
        '''
        NOTE: Please, check the keys of your dicts to be basic types only
        '''
        return cls.dumps(
            [
                pair
                for pair in inspect.getmembers(
                    obj, lambda m: not callable(m)
                )
                if not pair[0].startswith('_')
            ]
        )

    @classmethod
    def loads_object(cls, json_text):
        instance = ProcessorResults()
        for key, value in cls.loads(json_text):
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
        self.complete_worker = lambda x: x

        self.results_dir = results_dir
        if self.results_dir:
            self.created_dirs = set()
            shutil.rmtree(self.results_dir, ignore_errors=True)

    def get_result_file_path(self, dte):
        if not self.results_dir:
            raise Exception('Results dir is not set to use this method')

        month_dir = os.path.join(
            self.results_dir, str(dte.year), str(dte.month)
        )
        if month_dir not in self.created_dirs:
            try:
                os.makedirs(month_dir)
                self.created_dirs.add(month_dir)
            except OSError:
                pass
        return os.path.join(month_dir, str(dte.day))

    def extract_date_from_path(self, path):
        dte = ''.join(map(
            lambda s: s.zfill(2),
            path.split('/')[-3:])
        )
        return str2date(dte)

    def add(self, processor_results):
        raise NotImplementedError()

    @staticmethod
    def save_day(iterable, fname=None, mode='w'):
        with open(fname, mode) as fout:
            for obj in iterable:
                fout.write(FileProtocol.dumps(obj) + '\n')

    @staticmethod
    def load_day(fname):
        with open(fname) as fin:
            for line in fin:
                yield FileProtocol.loads(line)

    def iterate_saved_days(self):
        for root, dirs, fnames in os.walk(self.results_dir):
            for fn in fnames:
                yield os.path.join(root, fn)

    def complete(self, pool=None):
        engine = itertools.imap
        if pool:
            engine = pool.imap_unordered

        for _ in engine(
                self.complete_worker,
                self.iterate_saved_days()):
            pass


class ResultProcessor(object):
    def __init__(self, collector):
        self.collector = collector

    # look at print_stats for results format
    def gen_stats(self):
        raise NotImplementedError()

    def print_stats(self):
        for header, stats in self.gen_stats():
            print '-' * 20
            print header
            print '-' * 20
            for row in stats:
                print '\t'.join(map(unicode, row))
            print


def process_all(data_dir, results_dir, plugin,
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

        collector = load_plugin(plugin).ResultCollector(results_dir)
        for results in pool.imap_unordered(invoke_cmd_worker, items):
            collector.add(ProcessorResults.loads_object(results))

        logger = multiprocessing.get_logger()

        logger.info('Collector: completing')
        collector.complete(pool)
        logger.info('Collector: done')
    finally:
        pool.terminate()
        pool.join()

    return collector


def run(plugin_name, start_date, end_date,
        data_dir='/mnt/disk1/alohalytics/by_date',
        results_dir='/home/a.vodolazskiy/stats'):
    collector = process_all(
        data_dir, results_dir, plugin_name,
        start_date, end_date
    )
    stats = load_plugin(plugin_name).ResultProcessor(collector)

    logger = multiprocessing.get_logger()
    logger.info('Stats: processing')
    stats.print_stats()
    logger.info('Stats: done')


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
