import time

from PyQt4.QtGui import *

from lldbvis.debug import debugger
from lldbvis.events import signals
from lldbvis.events import dispatcher
from lldbvis.util.log import LogLevel


class ConsoleWidget(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.setLayout(QVBoxLayout())

        self.console_edit = QPlainTextEdit()
        self.console_edit.setWordWrapMode(QTextOption.WordWrap)
        self.console_edit.setReadOnly(True)

        self.layout().addWidget(self.console_edit, 0)

        dispatcher.connect(self.updateWidget, signal=signals.LogDebugger)
        dispatcher.connect(self.clear, signal=signals.StartDebugger)
        dispatcher.connect(self.__fakeResize, signal=signals.EndDebugger)

    def __fakeResize(self, *args, **kwargs):
        # used to prevent a segmentation fault
        parent = self.parent()
        while parent:
            parent = self.parent()
        s = parent.size()
        parent.resize(s)

    def updateWidget(self, *args, **kwargs):
        while not debugger.is_log_empty():
            log_item = debugger.consume_log()
            self.write(log_item[0], log_item[1])

        time.sleep(0.05)
        self.console_edit.update()
        time.sleep(0.05)

    def clear(self, *args, **kwargs):
        self.console_edit.clear()

    def write(self, msg, log_level=LogLevel.INFO):
        if log_level == LogLevel.INFO:
            self.writeInfo(msg)
        elif log_level == LogLevel.WARNING:
            self.writeWarning(msg)
        elif log_level == LogLevel.ERROR:
            self.writeError(msg)

    def writeLine(self, msg, log_level=LogLevel.INFO):
        self.write(msg, log_level)
        self.newLine()

    def writeInfo(self, msg):
        msgs = msg.splitlines()
        for m in msgs:
            m = "<span style='color: #ffffff;'>" + m + "</span>"
            self.console_edit.appendHtml(m)

    def writeWarning(self, msg):
        msgs = msg.splitlines()
        for m in msgs:
            m = "<span style='color: #ffff00;'>" + m + "</span>"
            self.console_edit.appendHtml(m)

    def writeError(self, msg):
        msgs = msg.splitlines()
        for m in msgs:
            m = "<span style='color: #ff0000;'>" + m + "</span>"
            self.console_edit.appendHtml(m)

    def newLine(self):
        self.console_edit.appendPlainText('\n')
