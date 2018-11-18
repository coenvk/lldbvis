from lldbvis.meta import Singleton

_connections = {}  # { id(sender) : { signal : [callbacks] } }


class Signal(object):
    def __init__(self):
        pass


class _AnySender(Signal):
    __metaclass__ = Singleton


class _AnySignal(Signal):
    __metaclass__ = Singleton


AnySender = _AnySender()
AnySignal = _AnySignal()

_id_any_sender = id(AnySender)

Before = 0
After = 1


class Signal:
    def __init__(self, name=None):
        self.name = name

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if isinstance(other, Signal):
            if self.name is None:
                return False
            return self.name == other.name
        else:
            return False

    def connect(self, callback, sender=AnySender):
        connect(callback, self, sender=sender)

    def disconnect(self, callback, sender=AnySender):
        disconnect(callback, self, sender=sender)

    def send(self, sender=AnySender, *args, **kwargs):
        _called(sender, self, *args, **kwargs)


def send(signal, when=After):
    def wrap(sender):
        def wrapper(*args, **kwargs):
            if when == After:
                ret = sender(*args, **kwargs)
                _called(sender, signal, *args, **kwargs)
            else:
                _called(sender, signal, *args, **kwargs)
                ret = sender(*args, **kwargs)
            return ret

        return wrapper

    return wrap


def connect(callback, signal=AnySignal, sender=AnySender):
    if isinstance(signal, (list, tuple)):
        for sig in signal:
            connect(callback, signal=sig, sender=sender)

    else:
        sender_id = id(sender)
        if sender_id not in _connections:
            _connections[sender_id] = {}
        signals = _connections[sender_id]
        if signal not in signals:
            signals[signal] = []
        signals[signal].append(callback)


def disconnect(callback, signal=AnySignal, sender=AnySender):
    if isinstance(signal, (list, tuple)):
        for sig in signal:
            disconnect(callback, signal=sig, sender=sender)

    else:
        sender_id = id(sender)
        if sender_id in _connections:
            signals = _connections[sender_id]
            callbacks = signals[signal]
            if callback in callbacks:
                callbacks.remove(callback)
            if not callbacks:
                del signals[signal]
            if not signals:
                del _connections[sender_id]


def _called(sender, signal=AnySignal, *args, **kwargs):
    if isinstance(signal, (list, tuple)):
        for sig in signal:
            _called(sender, signal=sig, *args, **kwargs)

    else:

        def _execute_callback(*args, **kwargs):
            try:
                callback(*args, **kwargs)
            except TypeError:
                try:
                    nargs = callback.__code__.co_argcount
                    if len(args) <= nargs:
                        callback(*args)
                    else:
                        callback()
                except AttributeError or TypeError:
                    callback()

        sender_id = id(sender)
        if sender_id in _connections:
            signals = _connections[sender_id]
            if signal in signals:
                for callback in signals[signal]:
                    _execute_callback(*args, **kwargs)

        if _id_any_sender in _connections:
            signals = _connections[_id_any_sender]
            if signal in signals:
                for callback in signals[signal]:
                    _execute_callback(*args, **kwargs)
