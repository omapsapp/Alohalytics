import importlib
import logging
import multiprocessing
import os
import subprocess
import sys
import argparse

from pyaloha.ccode import iterate_events


def setup_logs(filepath='py_alohalytics_stats.log'):
    logger = multiprocessing.get_logger()

    handler = logging.FileHandler(filepath)
    handler.setFormatter(logging.Formatter(fmt='%(asctime)-15s %(message)s'))
    logger.addHandler(handler)

    logger.setLevel(logging.INFO)


def load_plugin(plugin_name, plugin_dir):
    sys.path.append(plugin_dir)
    return importlib.import_module(plugin_name)


def invoke_cmd_worker(item):
    logger = multiprocessing.get_logger()
    try:
        pid = multiprocessing.current_process().pid

        plugin_dir, plugin, filepath, events_limit = item
        worker_fpath = os.path.abspath(__file__)
        cmd = 'gzip -d -c %s | python2.7 %s %s %s %s' % (
            filepath, worker_fpath, plugin_dir, plugin, events_limit
        )
        logger.info(
            '%d: Starting job: %s', pid, cmd
        )

        env = os.environ.copy()
        env['PYTHONPATH'] = os.pathsep.join(sys.path)

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, shell=True,
            env=env, close_fds=True
        )
        output = process.communicate()[0]
        logger.info(
            '%d: Got %0.2f Mbytes result from a job: %s',
            pid, float(len(output)) / 1000**2, cmd
        )
        return filepath, output
    except Exception as e:
        logger.exception('Worker launcher failed:\n %s', e)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'plugin_dir',
        help='Plugin directory. In most cases, `pyscripts`',
    )
    parser.add_argument(
        'plugin',
        help='Name of plugin to search in `plugin_dir`. Typically, these are just names of .py files. '
             'Examples: `userbase`, `locale_export`',
    )
    parser.add_argument(
        'events_limit', type=int, nargs='?',
        help='Read only first N events. If not specified, will read all events',
        default=0
    )
    return parser.parse_args()


def worker():
    setup_logs()
    logger = multiprocessing.get_logger()
    args = parse_args()

    try:
        processor = load_plugin(
            args.plugin, plugin_dir=args.plugin_dir
        ).DataStreamWorker()
        iterate_events(processor, events_limit=args.events_limit)
        processor.pre_output()
        sys.stdout.write(processor.dumps_results() + '\n')
        sys.stdout.flush()
    except Exception as e:
        logger.exception('Worker process failed:\n %s', e)


if __name__ == '__main__':
    worker()
