import os

from PyQt4.QtGui import *
from PyQt4.QtCore import QThread

from lldbvis.debug import debugger
from lldbvis.events import signals
from lldbvis.events import dispatcher
from lldbvis.gui.widgets import CodeEditor
from lldbvis.settings import constants


class DebugThread(QThread):
    def __init__(self, target, parent=None, *args):
        QThread.__init__(self, parent=parent)

        if not callable(target):
            raise TypeError('Thread target must be a callable')

        self.target = target
        self.args = args

    def run(self):
        if len(self.args) > 0:
            self.target(*self.args)
        else:
            self.target()


class RunArgumentsDialog(QDialog):
    def __init__(self, parent=None, *args):
        QWidget.__init__(self, parent, *args)

        self.setLayout(QFormLayout())

        self.fileName = None

        self.fileNameEdit = QLineEdit()
        self.fileNameEdit.textChanged.connect(self._checkExecutable)
        self.fileButton = QPushButton('Select File')
        self.fileButton.clicked.connect(self.selectFile)
        self.layout().addRow(self.fileButton, self.fileNameEdit)

        self.errorLabel = QLabel()
        self.errorLabel.setStyleSheet('color: red')
        self.layout().addRow(self.errorLabel)
        self.errorLabel.hide()

        button_box = QDialogButtonBox(self)
        button_box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.okButton = button_box.button(QDialogButtonBox.Ok)
        self.okButton.clicked.connect(lambda: [self.setFileName(), self.close()])
        self.cancelButton = button_box.button(QDialogButtonBox.Cancel)
        self.cancelButton.clicked.connect(lambda: [self.resetFileName(), self.close()])
        self.layout().addRow(button_box)

        self.setWindowTitle('Run Arguments')
        self.resize(constants.RUN_ARGUMENTS_DIALOG_SIZE)

    def _checkExecutable(self, file_path):
        if self._isExecutable(file_path):
            if not self.errorLabel.isHidden():
                self.errorLabel.hide()
            self.okButton.setEnabled(True)
        else:
            self.errorLabel.setText('File is not an executable!')
            self.okButton.setEnabled(False)
            self.errorLabel.show()

    def _isExecutable(self, file_path):
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

    def setFileName(self):
        self.fileName = self.fileNameEdit.text()

    def resetFileName(self):
        self.fileName = None

    def selectFile(self):
        file_dialog = QFileDialog()
        file_name = file_dialog.getOpenFileName(self, 'Select File')
        if file_name is not None and os.path.isfile(file_name):
            self.fileNameEdit.setText(file_name)

    def getFileName(self):
        return str(self.fileName)


class VisWindow(QMainWindow):
    def __init__(self, *argv):
        QMainWindow.__init__(self, *argv)
        self.debugThread = None

        self.targetFile = None
        self.workingDir = None

        self.editor = CodeEditor()

        self.runAction = None
        self.runMenu = None
        self.createMenuBar()
        self.runArgumentsDialog = RunArgumentsDialog()

        dispatcher.connect(lambda *args, **kwargs: self.runMenu.setEnabled(True), signal=signals.EndDebugger)
        dispatcher.connect(self.openDeclaration, signal=signals.OpenDeclaration)

    def createMenuBar(self):
        mb = self.menuBar()

        self.runAction = QAction('Run', self)
        self.runAction.setDisabled(self.targetFile is None)
        self.runAction.setShortcut('Shift+F10')
        self.runAction.triggered.connect(self.runDebugger)

        run_config_action = QAction('Set Run Arguments...', self)
        run_config_action.triggered.connect(lambda: [self.setRunArguments(), self.enableRunAction()])

        open_editor_action = QAction('Open Editor', self)
        open_editor_action.triggered.connect(self.openEditor)

        self.runMenu = mb.addMenu('Run')
        self.runMenu.addAction(self.runAction)
        self.runMenu.addAction(run_config_action)

        editor_menu = mb.addMenu('Editor')
        editor_menu.addAction(open_editor_action)

    def openDeclaration(self, file_name, line):
        self.openEditor()
        self.editor.tabbed_editor.openFile(file_name)
        try:
            self.editor.tabbed_editor.currentWidget().scrollToLine(line)
        except Exception:
            pass

    def openEditor(self):
        if self.editor.isHidden():
            self.editor.show()
        else:
            self.editor.raise_()
            self.editor.activateWindow()

    def runDebugger(self):
        debugger.setup(self.workingDir, self.targetFile)
        self.debugThread = DebugThread(parent=self, target=debugger.start)
        self.debugThread.setTerminationEnabled(True)
        self.debugThread.start()
        self.runMenu.setEnabled(False)

    def enableRunAction(self, *args, **kwargs):
        if self.targetFile is not None:
            self.runAction.setEnabled(True)
            self.runAction.setText("Run '" + str(self.targetFile) + "'")

    def setRunArguments(self):
        self.runArgumentsDialog.exec_()
        file_path = self.runArgumentsDialog.getFileName()
        if file_path is not None and os.path.isfile(file_path):
            file_name = os.path.basename(file_path)
            self.workingDir = file_path.replace(file_name, '')
            self.targetFile = file_name
