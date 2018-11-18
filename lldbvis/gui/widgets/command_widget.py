from PyQt4.QtGui import *
from PyQt4.QtCore import *
from lldbvis.debug import debugger
from lldbvis.settings import constants


class CommandWidget(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.setLayout(QVBoxLayout())

        self.execute_button = None
        self.backtrace_cmd_button = None
        self.tb = self._createToolbar()

        self.layout().addWidget(self.tb, 0, Qt.AlignLeading)

        self.command_edit = QLineEdit()
        self.layout().addWidget(self.command_edit, 0, Qt.AlignTop)
        self.command_edit.returnPressed.connect(self.execute_button.click)

        self.command_result = QTextEdit()
        self.command_result.setReadOnly(True)
        self.layout().addWidget(self.command_result, 0)

    def _createToolbar(self):
        tb = QToolBar()

        self.execute_button = QToolButton()
        self.execute_button.setText('Execute')
        self.execute_button.clicked.connect(self.execute)

        self.backtrace_cmd_button = QToolButton()
        self.backtrace_cmd_button.setText('thread backtrace')
        self.backtrace_cmd_button.clicked.connect(lambda: self.execute_cmd_button(self.backtrace_cmd_button))
        self.backtrace_cmd_button.setStyleSheet('padding: 0;')

        self.bp_list_cmd_button = QToolButton()
        self.bp_list_cmd_button.setText('breakpoint list')
        self.bp_list_cmd_button.clicked.connect(lambda: self.execute_cmd_button(self.bp_list_cmd_button))
        self.bp_list_cmd_button.setStyleSheet('padding: 0;')

        self.fr_variable_cmd_button = QToolButton()
        self.fr_variable_cmd_button.setText('frame variable')
        self.fr_variable_cmd_button.clicked.connect(lambda: self.execute_cmd_button(self.fr_variable_cmd_button))
        self.fr_variable_cmd_button.setStyleSheet('padding: 0;')

        self.ta_variable_cmd_button = QToolButton()
        self.ta_variable_cmd_button.setText('target variable')
        self.ta_variable_cmd_button.clicked.connect(lambda: self.execute_cmd_button(self.ta_variable_cmd_button))
        self.ta_variable_cmd_button.setStyleSheet('padding: 0;')

        self.thread_list_cmd_button = QToolButton()
        self.thread_list_cmd_button.setText('thread list')
        self.thread_list_cmd_button.clicked.connect(lambda: self.execute_cmd_button(self.thread_list_cmd_button))
        self.thread_list_cmd_button.setStyleSheet('padding: 0;')

        self.frame_info_cmd_button = QToolButton()
        self.frame_info_cmd_button.setText('frame info')
        self.frame_info_cmd_button.clicked.connect(lambda: self.execute_cmd_button(self.frame_info_cmd_button))
        self.frame_info_cmd_button.setStyleSheet('padding: 0;')

        cmd_box = QWidget()
        box_layout = QHBoxLayout()
        cmd_box.setLayout(box_layout)
        cmd_box.setStyleSheet('padding: 0; margin: 0;')

        spacer = QSpacerItem(constants.COMMANDS_CATEGORY_H_SPACE, 0, QSizePolicy.Maximum)
        box_layout.addWidget(self.ta_variable_cmd_button)
        box_layout.addSpacerItem(spacer)
        box_layout.addWidget(self.thread_list_cmd_button)
        box_layout.addWidget(self.backtrace_cmd_button)
        box_layout.addSpacerItem(spacer)
        box_layout.addWidget(self.frame_info_cmd_button)
        box_layout.addWidget(self.fr_variable_cmd_button)
        box_layout.addSpacerItem(spacer)
        box_layout.addWidget(self.bp_list_cmd_button)

        tb.addWidget(self.execute_button)
        tb.addSeparator()
        tb.addWidget(cmd_box)
        return tb

    def execute_cmd_button(self, cmd_button):
        cmd = cmd_button.text()
        self.command_edit.setText(cmd)
        self.execute()

    def execute(self):
        cmd = self.command_edit.text()
        res = debugger.execute_command(str(cmd))
        self.command_result.clear()

        if res.Succeeded():
            self.command_result.append(res.GetOutput())

        else:
            error_string = "Command did not succeed to execute!"
            self.command_result.setTextColor(constants.ERROR_TEXT_COLOR)
            self.command_result.append(error_string)
            self.command_result.setTextColor(constants.DEFAULT_TEXT_COLOR)

