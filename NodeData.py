from Debugger import Debugger
from lldb import *


class NodeData(object):
    def __init__(self, name=''):
        self.debugger = Debugger()
        self.name = name

    def __str__(self):
        return self.name

    @property
    def description(self):
        raise NotImplementedError

    @classmethod
    def dataType(cls):
        raise NotImplementedError


def NodeDataFactory(debugObject):
    for cls in NodeData.__subclasses__():
        if isinstance(debugObject, cls.dataType()):
            return cls(debugObject)


class ProcessData(NodeData):
    def __init__(self, process=None, name=''):
        NodeData.__init__(self, name)
        self.setTo(process)

    def setTo(self, process):
        if process is not None:
            self.name = process.GetProcessInfo().GetExecutableFile().GetFilename()

    @property
    def description(self):
        return self.name

    @classmethod
    def dataType(cls):
        return SBProcess


class ThreadData(NodeData):
    def __init__(self, thread=None, name=''):
        NodeData.__init__(self, name)
        self.setTo(thread)

    def setTo(self, thread):
        if thread is not None:
            self.name = thread.GetName()

    @property
    def description(self):
        return self.name

    @classmethod
    def dataType(cls):
        return SBThread


class FrameData(NodeData):
    def __init__(self, frame=None, name=''):
        NodeData.__init__(self, name)
        self.setTo(frame)

    def setTo(self, frame):
        if frame is not None:
            self.name = frame.GetDisplayFunctionName()

    @property
    def description(self):
        return self.name

    @classmethod
    def dataType(cls):
        return SBFrame


class ValueData(NodeData):
    def __init__(self, value=None, name=''):
        NodeData.__init__(self, name)
        self.setTo(value)

    def setTo(self, value):
        if value is not None:
            self.name = value.GetName()

    @property
    def description(self):
        return self.name

    @classmethod
    def dataType(cls):
        return SBValue
