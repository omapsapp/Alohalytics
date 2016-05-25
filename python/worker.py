#!/bin/env python2.7

import importlib
import logging
import multiprocessing
import os
import subprocess
import sys
import traceback

from ccode import iterate_events


def setup_logs(filepath=os.path.join('/tmp', 'py_alohalytics_stats.log')):
    logger = multiprocessing.get_logger()

    handler = logging.FileHandler(filepath)
    handler.setFormatter(logging.Formatter(fmt='%(asctime)-15s %(message)s'))
    logger.addHandler(handler)

    logger.setLevel(logging.INFO)


def load_plugin(plugin_name):
    return importlib.import_module('snippets.%s' % plugin_name)


def invoke_cmd_worker(item):
    try:
        logger = multiprocessing.get_logger()
        pid = multiprocessing.current_process().pid

        plugin, filepath = item
        cmd = 'gzip -d -c %s | ./worker.py %s' % (
            filepath, plugin
        )
        logger.info(
            '%d: Starting job: %s', pid, cmd
        )

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, shell=True
        )
        output = process.communicate()[0]
        return output
    except Exception as e:
        traceback.print_exc(e)


def worker():
    setup_logs()
    try:
        plugin = sys.argv[1]
        processor = load_plugin(plugin).StreamProcessor()
        iterate_events(processor)
        processor.finish()
        print processor.dumps_results()
    except Exception:
        logger = multiprocessing.get_logger()
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    worker()
