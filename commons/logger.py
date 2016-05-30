# -*- coding: utf-8 -*-
import logging
from os.path import isfile
from datetime import datetime
import settings as config

__author__ = 'whoami'
__version__ = '0.0.0'
__date__ = '27.03.16 0:46'
__description__ = """
Оборачиваем работу проекта в лог
"""


class SingletonMetaclass(type):
    """
    Метаксласс для разовой инициализации класса Logger и возврата
    объекта логгера
    """
    def __init__(cls, *args, **kw):
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(
                SingletonMetaclass, cls).__call__(*args, **kw)
        return cls.instance


class Logger(metaclass=SingletonMetaclass):
    def __init__(self):
        log_msg_format = '%(asctime)s.%(msecs)d %(levelname)s in ' \
                         '\'%(module)s\' at line %(lineno)d: %(message)s'

        level = logging.DEBUG if config.debug else logging.INFO

        log_filename = config.log_dir + '{}.log'.format(str(datetime.now()))
        formatter = logging.Formatter(log_msg_format)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)

        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(formatter)

        self.logger.addHandler(console)
        if not isfile(log_filename):
            try:
                with open(log_filename, 'w') as _:
                    pass
                file_handler = logging.FileHandler(log_filename)
                file_handler.setFormatter(formatter)
                file_handler.setLevel(level)
                self.logger.addHandler(file_handler)
            except Exception:
                pass

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def debug(self, msg):
        self.logger.debug(msg)
