#!/bin/env python2.7

# This helper cmd run script is to be used like:
# ./pysnip/run <pyscript_name> <params>
# It will take care of PYTHONPATH and plugin_dir
# and start pyaloha with specified script and params

import os
import sys

base_path = os.path.dirname(os.path.abspath(__file__))

pyaloha_path = os.path.join(
    base_path, '..', '..',
    'Alohalytics', 'snippets'
)
pysnip_path = os.path.join(
    base_path, '..'
)
sys.path.extend([pyaloha_path, pysnip_path])

PYSCRIPT_PATH = os.path.join(
    base_path, '..', 'pyscripts'
)

ALOHA_DATA = os.environ['ALOHA_DATA_DIR']

if __name__ == '__main__':
    pyaloha = __import__('pyaloha.main')
    pyaloha.main.cmd_run(plugin_dir=PYSCRIPT_PATH, data_dir=ALOHA_DATA)
