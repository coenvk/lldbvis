from Metaclasses import Singleton
import functools


def observable(func):
    def update(obj, *args, **kwargs):
        func(obj, *args, **kwargs)
        Observer().called(obj, func.__name__, *args, **kwargs)
    functools.update_wrapper(update, func)
    return update


class Observer:
    __metaclass__ = Singleton

    def __init__(self):
        self._obversables = {}

    def add(self, observable, method, callback):
        if observable not in self._obversables:
            self._obversables[observable] = {}
        methods = self._obversables[observable]
        if method not in methods:
            methods[method] = []
        methods[method].append(callback)

    def called(self, observable, method, *args, **kwargs):
        if observable in self._obversables:
            methods = self._obversables[observable]
            if method in methods:
                for callback in methods[method]:
                    callback(*args, **kwargs)
