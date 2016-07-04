#!/bin/env python2.7

# This a helper cmd run script to be used like:
# ./pysnip/run <pyscript_name>
# It will take care of PYTHONPATH and plugin_path

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

if __name__ == '__main__':
    pyaloha = __import__('pyaloha.main')
    pyaloha.main.cmd_run(plugin_dir=PYSCRIPT_PATH)
