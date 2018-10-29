from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
from Debugger import Debugger
from Observer import Observer


class VariableWidget(QWidget):
    def __init__(self, widget, *args):
        QWidget.__init__(self, *args)
        self.debugger = Debugger()
        self.setLayout(QVBoxLayout())
        self.collapseButton = QCheckBox('Collapsed')
        self.collapseButton.toggled.connect(self.collapseNode)
        self.layout().addWidget(self.collapseButton, 0, Qt.AlignLeading | Qt.AlignRight)
        self.label = QLabel('')
        self.label.setWordWrap(True)
        self.layout().addWidget(self.label, 0, Qt.AlignTop)

        self.setEnabled(False)

        self.widget = widget
        Observer().add(self.widget, 'selectedId', self.updateWidget)

        Observer().add(self.debugger, 'setup', self.enable)
        Observer().add(self.debugger, 'pause', self.updateWidget)
        Observer().add(self.debugger, 'end', self.disable)

    def disable(self, *args, **kwargs):
        self.setEnabled(False)
        self.collapseButton.setChecked(False)
        self.label.clear()

    def enable(self, *args, **kwargs):
        self.setEnabled(True)

    def collapseNode(self, checked):
        self.widget.selectedNode().geom.collapsed = checked

    def updateWidget(self, *args, **kwargs):
        sel_node = self.widget.selectedNode()

        self.collapseButton.setChecked(sel_node.geom.collapsed)

        self.label.setText(sel_node.data.description)


