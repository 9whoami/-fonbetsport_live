# -*- coding: utf-8 -*-
import os
from configparser import ConfigParser


def read_cfg(cfg_file='settings.cfg', section='base'):
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(cfg_file)

    # get section, default to mysql
    cfg = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            cfg[item[0]] = item[1]
    else:
        raise Exception(
            '{0} not found in the {1} file'.format(section, cfg_file))

    return cfg


def config_file():
    from settings import namespace
    cfg = read_cfg()
    for key in namespace.argv_var:
        value = cfg.get(key, namespace.__dict__[key])
        namespace.__dict__[key] = value
        try:
            namespace.argv_var[key]['default'] = value
        except (KeyError, AttributeError):
            pass


def sys_argv():
    from .argvparser import create_parser
    from settings import namespace
    arguments = create_parser()

    for key in namespace.argv_var:
        namespace.__dict__[key] = getattr(arguments, key)


def load_settings(from_config_file=False, from_sys_argv=False):
    if from_config_file:
        config_file()
    if from_sys_argv:
        sys_argv()
