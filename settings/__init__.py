# -*- coding: utf-8 -*-
from .commons import load_settings
load_settings(from_sys_argv=True, from_config_file=False)

from .namespace import *

if not send_to_url and not save_to_file:
    from .argvparser import create_parser
    from os import sys
    sys.argv = ['', '--help']
    print('Необходимо указать параметр для сохранения json')
    create_parser()
