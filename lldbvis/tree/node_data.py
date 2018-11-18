from lldb import *

from lldbvis.util.formatters import format_value, format_frame


class NodeData(object):
    def __init__(self, name=''):
        self.name = name
        self.id = None

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
        if process is not None and process.IsValid():
            self.name = process.GetProcessInfo().GetExecutableFile().GetFilename()
            self.id = process.GetProcessID()

    @property
    def description(self):
        descr = 'Target Filename: ' + str(self.name)
        return descr.rstrip()

    @classmethod
    def dataType(cls):
        return SBProcess


class ThreadData(NodeData):
    def __init__(self, thread=None, name=''):
        NodeData.__init__(self, name)
        self.setTo(thread)

    def setTo(self, thread):
        if thread is not None and thread.IsValid():
            self.name = thread.GetName()
            self.id = thread.GetThreadID()

    @property
    def description(self):
        descr = 'Name: ' + str(self.name)
        return descr.rstrip()

    @classmethod
    def dataType(cls):
        return SBThread


class FrameData(NodeData):
    def __init__(self, frame=None, name=''):
        NodeData.__init__(self, name)
        self.tuple = None
        self.setTo(frame)

    def setTo(self, frame):
        if frame is not None and frame.IsValid():
            self.id = frame.GetFrameID()
            self.tuple = format_frame(frame)
            self.name = self.tuple.name

    @property
    def return_type_name(self):
        return self.tuple.return_type_name

    @property
    def description(self):
        descr = 'Name: ' + str(self.name) + '\n'
        descr += 'Return Type: ' + str(self.return_type_name) + '\n'
        descr += 'Address: ' + "0x%16x" % int(self.address)
        return descr.rstrip()

    @property
    def address(self):
        return self.tuple.address

    @property
    def arguments(self):
        arg_names = self.tuple.arg_names
        arg_type_names = self.tuple.arg_type_names
        arg_values = self.tuple.arg_values
        args = zip(arg_names, arg_type_names, arg_values)
        return args

    @classmethod
    def dataType(cls):
        return SBFrame


class ValueData(NodeData):
    def __init__(self, value=None, name=''):
        NodeData.__init__(self, name)
        self.tuple = None
        self.declaration = None
        self.setTo(value)

    def setTo(self, value):
        if value is not None and value.IsValid():
            self.id = value.GetID()
            self.tuple = format_value(value)
            self.name = self.tuple.name
            self.declaration = value.GetDeclaration()

    @property
    def type_name(self):
        return self.tuple.type_name

    @property
    def value(self):
        return self.tuple.value

    @property
    def address(self):
        return self.tuple.address

    @property
    def byte_size(self):
        return self.tuple.byte_size

    @property
    def description(self):
        descr = 'Name: ' + str(self.name) + '\n'
        descr += 'Type: ' + str(self.type_name) + '\n'
        if self.value is not None:
            descr += 'Value: ' + str(self.value) + '\n'
        descr += 'Address: ' + "0x%16x" % int(self.address) + '\n'
        descr += 'Byte Size: ' + str(self.byte_size)
        return descr.rstrip()

    @classmethod
    def dataType(cls):
        return SBValue
