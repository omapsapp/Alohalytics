#!/bin/env python2.7

# This helper cmd run script is to be used like:
# ./pysnip/run <pyscript_name> <params>
# It will take care of PYTHONPATH and plugin_dir
# and start pyaloha with specified script and params

import tracemalloc
tracemalloc.start()

from .run import PYSCRIPT_PATH

if __name__ == '__main__':
    pyaloha = __import__('pyaloha.main')
    pyaloha.main.cmd_run(plugin_dir=PYSCRIPT_PATH)

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print("[ Top 10 ]")
    for stat in top_stats[:10]:
        print(stat)
