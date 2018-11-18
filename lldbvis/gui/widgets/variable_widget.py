from PyQt4.QtGui import *

from lldbvis.events import signals
from lldbvis.events import dispatcher


class MemberOfSubWidget(QListWidget):
    def __init__(self, parent):
        QListWidget.__init__(self, parent)

        self.member_of = None
        self.setFixedHeight(20)

    def setMemberOf(self, member_of):
        self.clear()
        self.member_of = member_of
        self.addItem(self.member_of.name)


class MembersSubWidget(QListWidget):
    def __init__(self, parent):
        QListWidget.__init__(self, parent)

        self.members = {}

    def setMembers(self, members):
        self.clear()
        self.addMembers(members)

    def addMembers(self, members):
        if isinstance(members, (list, tuple)):
            for member in members:
                self.addMembers(member)
        else:
            self.members[members.name] = members
            self.addItem(members.name)


class VariableWidget(QWidget):
    def __init__(self, vis_widget, *args):
        QWidget.__init__(self, *args)
        self.vis_widget = vis_widget

        self.setLayout(QFormLayout())

        self.collapse_button = QCheckBox('Collapsed')
        self.collapse_button.toggled.connect(self.collapseNode)
        self.layout().addWidget(self.collapse_button)

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.layout().addWidget(self.description_label)

        self.func_args_label = QLabel()
        self.func_args_label.setText('Arguments')
        self.layout().addWidget(self.func_args_label)
        self.func_args_table = QTableWidget()
        self.func_args_table.setColumnCount(3)
        self.func_args_label.hide()
        self.func_args_table.hide()
        self.layout().addWidget(self.func_args_table)

        self.member_of_widget = MemberOfSubWidget(self)
        self.member_of_label = QLabel('Member Of')
        self.layout().addWidget(self.member_of_label)
        self.layout().addWidget(self.member_of_widget)
        self.member_of_label.hide()
        self.member_of_widget.hide()
        self.member_of_widget.itemClicked.connect(self.changeToMemberOfNode)

        self.members_widget = MembersSubWidget(self)
        self.members_label = QLabel('Members')
        self.layout().addWidget(self.members_label)
        self.layout().addWidget(self.members_widget)
        self.members_widget.itemClicked.connect(self.changeToMemberNode)

        self.open_declaration_button = QPushButton('Open Declaration', self)
        self.open_declaration_button.hide()
        self.layout().addWidget(self.open_declaration_button)
        self.open_declaration_button.clicked.connect(self.openDeclaration)

        self.setEnabled(False)

        dispatcher.connect(self.updateWidget, signal=[signals.SelectNode, signals.PauseDebugger])
        dispatcher.connect(self.enable, signal=signals.SetupDebugger)
        dispatcher.connect(self.disable, signal=signals.EndDebugger)

    def disable(self, *args, **kwargs):
        self.setEnabled(False)
        self.collapse_button.setChecked(False)
        self.description_label.clear()

    def enable(self, *args, **kwargs):
        self.setEnabled(True)

    def toggleExtraInfo(self, checked):
        self.extra_info_widget.setHidden(not checked)

    def collapseNode(self, checked):
        self.vis_widget.selectedNode().geom.collapsed = checked

    def openDeclaration(self, checked):
        node = self.vis_widget.selectedNode()
        if node.isValueNode():
            declaration = node.data.declaration
            file_spec = declaration.GetFileSpec()

            file_name = file_spec.GetDirectory() + '/' + file_spec.GetFilename()
            line = declaration.GetLine()

            signals.OpenDeclaration.send(dispatcher.AnySender, file_name, line)

    def changeToMemberOfNode(self, item):
        self.vis_widget.selectedId = self.member_of_widget.member_of.id

    def changeToMemberNode(self, item):
        name = str(item.text())
        self.vis_widget.selectedId = self.members_widget.members[name].id

    def updateArgumentsWidget(self, *args, **kwargs):
        sel_node = self.vis_widget.selectedNode()

        if sel_node.isFrameNode():
            args = sel_node.data.arguments

            if len(args) == 0:
                self.func_args_label.hide()
                self.func_args_table.hide()

            else:
                self.func_args_table.clear()
                self.func_args_table.setHorizontalHeaderLabels(['Name', 'Type', 'Value'])

                rows = len(args)
                self.func_args_table.setRowCount(rows)
                for i in range(rows):
                    arg = args[i]
                    for j in range(len(arg)):
                        self.func_args_table.setItem(i, j, QTableWidgetItem(str(arg[j])))

                self.func_args_label.show()
                self.func_args_table.show()

        else:
            self.func_args_label.hide()
            self.func_args_table.hide()

    def updateDeclarationButton(self, *args, **kwargs):
        sel_node = self.vis_widget.selectedNode()

        if sel_node.isValueNode():
            self.open_declaration_button.show()

        else:
            self.open_declaration_button.hide()

    def updateWidget(self, *args, **kwargs):
        sel_node = self.vis_widget.selectedNode()

        self.collapse_button.setChecked(sel_node.geom.collapsed)

        parent = self.parent()
        if isinstance(parent, QDockWidget):
            if sel_node.isProcessNode():
                parent.setWindowTitle("Process")
            elif sel_node.isThreadNode():
                parent.setWindowTitle("Thread")
            elif sel_node.isFrameNode():
                parent.setWindowTitle("Frame")
            elif sel_node.isValueNode():
                parent.setWindowTitle("Variable")

        self.description_label.setText(sel_node.data.description)

        self.updateArgumentsWidget(args, kwargs)
        self.updateDeclarationButton(args, kwargs)

        if not sel_node.isRoot():
            self.member_of_widget.setMemberOf(sel_node.parent)
            if self.member_of_widget.isHidden():
                self.member_of_label.show()
                self.member_of_widget.show()
        elif not self.member_of_widget.isHidden():
            self.member_of_label.hide()
            self.member_of_widget.hide()

        self.members_widget.setMembers(sel_node.children)
