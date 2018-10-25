import sys
import os

import qdarkstyle
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Editor import DebugWidget
from FramesWidget import FramesWidget
from VariableWidget import VariableWidget
from VisWidget import VisWidget
from Debugger import Debugger

import threading


class RunArgumentsDialog(QDialog):
    def __init__(self, parent=None, *args):
        QWidget.__init__(self, parent, *args)

        self.setLayout(QFormLayout())

        self.fileName = None

        self.line = QLineEdit()
        self.fileButton = QPushButton('Select File')
        self.fileButton.clicked.connect(self.selectFile)
        self.layout().addRow(self.fileButton, self.line)

        button_box = QDialogButtonBox(self)
        button_box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.okButton = button_box.button(QDialogButtonBox.Ok)
        self.okButton.clicked.connect(lambda: [self.setFileName(), self.close()])
        self.cancelButton = button_box.button(QDialogButtonBox.Cancel)
        self.cancelButton.clicked.connect(lambda: [self.resetFileName(), self.close()])
        self.layout().addRow(button_box)

        self.setWindowTitle('Run Arguments')
        self.resize(500, 0)

    def setFileName(self):
        self.fileName = self.line.text()

    def resetFileName(self):
        self.fileName = None

    def selectFile(self):
        file_dialog = QFileDialog()
        file_name = file_dialog.getOpenFileName(self, 'Select File')
        if file_name is not None and os.path.isfile(file_name):
            self.line.setText(file_name)

    def getFileName(self):
        return str(self.fileName)


class VisWindow(QMainWindow):
    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.targetFile = None
        self.workingDir = None
        self.createMenuBar()
        self.runArgumentsDialog = RunArgumentsDialog()

    def createMenuBar(self):
        mb = self.menuBar()

        run_action = QAction('Run', self)
        run_action.setDisabled(self.targetFile is None)
        run_action.setShortcut('Shift+F10')
        run_action.triggered.connect(self.runDebugger)

        run_config_action = QAction('Set Run Arguments...', self)
        run_config_action.triggered.connect(lambda: [self.setRunArguments(), self.enableRunAction(run_action)])

        run_menu = mb.addMenu('Run')
        run_menu.addAction(run_action)
        run_menu.addAction(run_config_action)

    def runDebugger(self):
        debugger = Debugger()
        debugger.setup(self.workingDir, self.targetFile)
        debug_thread = threading.Thread(target=debugger.debugLoop, args=())
        debug_thread.start()

    def enableRunAction(self, runAction):
        if self.targetFile is not None:
            runAction.setEnabled(True)
            runAction.setText("Run '" + str(self.targetFile) + "'")

    def setRunArguments(self):
        self.runArgumentsDialog.exec_()
        file_path = self.runArgumentsDialog.getFileName()
        if file_path is not None and os.path.isfile(file_path):
            file_name = os.path.basename(file_path)
            self.workingDir = file_path.replace(file_name, '')
            self.targetFile = file_name


def main():
    app = QApplication(sys.argv)
    dark_stylesheet = qdarkstyle.load_stylesheet_from_environment()
    app.setStyleSheet(dark_stylesheet)

    window = VisWindow()

    widget = VisWidget()
    widget.resize(800, 600)

    editor = DebugWidget()
    frameWidget = FramesWidget()
    variableWidget = VariableWidget(widget)

    window.setCentralWidget(widget)

    bottomDockWidget = QDockWidget(window)
    bottomDockWidget.setFeatures(QDockWidget.DockWidgetMovable)
    bottomDockWidget.setWidget(editor)

    leftDockWidget = QDockWidget(window)
    leftDockWidget.setFeatures(QDockWidget.DockWidgetMovable)
    leftDockWidget.setWidget(frameWidget)
    leftDockWidget.setWindowTitle("Frames")

    rightDockWidget = QDockWidget(window)
    rightDockWidget.setFeatures(QDockWidget.DockWidgetMovable)
    rightDockWidget.setWidget(variableWidget)
    rightDockWidget.setWindowTitle("Variables")

    window.addDockWidget(Qt.BottomDockWidgetArea, bottomDockWidget)
    window.addDockWidget(Qt.LeftDockWidgetArea, leftDockWidget)
    window.addDockWidget(Qt.RightDockWidgetArea, rightDockWidget)
    window.resize(widget.size())
    window.setWindowTitle('LLDBVis')

    window.show()

    exit_code = app.exec_()
    sys.exit(exit_code)


if __name__ == '__main__':
    os.environ['QT_API'] = 'pyqt'
    main()
