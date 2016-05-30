# -*- coding: utf-8 -*-
from pyvirtualdisplay import Display
import settings as conf


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


class VirtualDisplay(metaclass=SingletonMetaclass):
    display = None
    trigger = conf.use_virtual_display

    def __init__(self):
        if not self.trigger:
            return

        try:
            self.display = Display()
            assert self.display
        except Exception as e:
            raise SystemError('Не удалось создать виртуальный дисплей {!r}'.format(e))

    def start(self):
        if isinstance(self.display, Display):
            self.display.start()

    def stop(self):
        if isinstance(self.display, Display):
            self.display.stop()

    def __del__(self):
        if isinstance(self.display, Display):
            self.display.stop()

    @staticmethod
    def on_virtual_display(fun):

        def wrapper(*args, **kwargs):
            display = VirtualDisplay()
            display.start()

            try:
                fun(*args, **kwargs)
            except Exception as e:
                print("При выполнении {!r} возникло "
                      "исключение с сообщением {!r}".format(fun.__name__, e))

            display.stop()

        return wrapper
