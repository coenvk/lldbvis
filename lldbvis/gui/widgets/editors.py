from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lldb import *

from lldbvis.util import resource_path
from lldbvis.util import bpl
from lldbvis.debug import debugger
from lldbvis.events import signals
from lldbvis.events import dispatcher
from lldbvis.settings import constants


class LineNumberArea(QWidget):
    def __init__(self, editor=None):
        QWidget.__init__(self, editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, QPaintEvent):
        self.editor.lineNumberAreaPaintEvent(QPaintEvent)

    def mousePressEvent(self, QMouseEvent):
        self.editor.lineNumberAreaMousePressEvent(QMouseEvent)


class Editor(QPlainTextEdit):
    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)

        self.file_path = None

        self.line_number_area = LineNumberArea(self)

        self.connect(self, SIGNAL('blockCountChanged(int)'), self.updateLineNumberAreaWidth)
        self.connect(self, SIGNAL('updateRequest(QRect,int)'), self.updateLineNumberArea)
        self.connect(self, SIGNAL('cursorPositionChanged()'), self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)

    def scrollToLine(self, line):
        self.moveCursor(QTextCursor.End)
        cursor = QTextCursor(self.document().findBlockByLineNumber(line - 1))
        self.setTextCursor(cursor)

    def openFile(self, file_name):
        if os.path.isfile(file_name):
            self.file_path = file_name
            f = open(file_name, 'r')
            with f:
                content = f.read()
                self.setPlainText(content)

    def clear(self):
        QPlainTextEdit.clear(self)
        self.file_path = None

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = constants.LINE_NUMBER_AREA_PADDING_LEFT + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, QResizeEvent):
        QPlainTextEdit.resizeEvent(self, QResizeEvent)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaMousePressEvent(self, QMouseEvent):
        pass

    def getBlockAtPoint(self, point):
        block = self.firstVisibleBlock()
        bounds = self.blockBoundingRect(block)

        while not bounds.top() <= point.y() <= bounds.height():
            block = block.next()
            bounds = self.blockBoundingRect(block)
            if not block.isValid():
                return None

        return block

    def getBlockAtIndex(self, index):
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()

        if blockNumber <= index:
            for i in range(block.blockNumber(), index):
                block = block.next()

        if block.isValid():
            return block

        return None

    def lineNumberAreaPaintEvent(self, QPaintEvent):
        painter = QPainter(self.line_number_area)
        bg_color = constants.LINE_NUMBER_AREA_BACKGROUND_COLOR
        painter.fillRect(QPaintEvent.rect(), bg_color)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        height = self.fontMetrics().height()
        while block.isValid() and (top <= QPaintEvent.rect().bottom()):
            if block.isVisible() and (bottom >= QPaintEvent.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(constants.LINE_NUMBER_AREA_FONT_COLOR)
                painter.drawText(0, top, self.line_number_area.width(), height, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []
        selection = QTextEdit.ExtraSelection()
        lineColor = constants.EDITOR_LINE_HIGHLIGHT_COLOR

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        extraSelections.append(selection)

        self.setExtraSelections(extraSelections)


class BreakpointsEditor(Editor):
    def __init__(self, tabbed_editor, *args):
        Editor.__init__(self, tabbed_editor, *args)
        self.tabbed_editor = tabbed_editor
        self.breakpoints = []

    def openFile(self, file_name):
        Editor.openFile(self, file_name)
        self.readBreakpoints(file_name)

    def readBreakpoints(self, file_name):
        bpl.read()
        self.breakpoints = bpl.get_breakpoints(file_name)

    def lineNumberAreaMousePressEvent(self, QMouseEvent):
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()

        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        height = self.blockBoundingRect(block).height()
        width = self.line_number_area.width()
        bottom = top + height

        while block.isValid():
            if top <= QMouseEvent.y() <= bottom and 0 <= QMouseEvent.x() <= width:

                self.tabbed_editor.addUnsavedTab(self)

                if blockNumber not in self.breakpoints:
                    self.breakpoints.append(blockNumber)
                elif blockNumber in self.breakpoints:
                    self.breakpoints.remove(blockNumber)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

        self.repaint()

    def lineNumberAreaPaintEvent(self, QPaintEvent):
        painter = QPainter(self.line_number_area)
        bg_color = constants.LINE_NUMBER_AREA_BACKGROUND_COLOR
        painter.fillRect(QPaintEvent.rect(), bg_color)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()

        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()
        while block.isValid() and (top <= QPaintEvent.rect().bottom()):

            if block.isVisible() and (bottom >= QPaintEvent.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(QColor(255, 255, 255, 120))
                painter.drawText(0, top, self.line_number_area.width(), height, Qt.AlignRight, number)

                if blockNumber in self.breakpoints:
                    painter.setBrush(Qt.red)
                    painter.drawEllipse(0, top + height / 8, 3 * height / 4, 3 * height / 4)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1


class CodeEditorWidget(QMainWindow):
    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.tabbed_editor = TabbedEditor(self)
        self.setCentralWidget(self.tabbed_editor)
        self.menu_bar = self.menuBar()

        self._save_action = None
        self._save_as_action = None
        self.createFileMenu()

        self.resize(constants.DEFAULT_WINDOW_SIZE)

    def createFileMenu(self):
        newAction = QAction('New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.tabbed_editor.newFile)

        openAction = QAction('Open...', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(lambda x: self.tabbed_editor.openFile())

        self._save_action = QAction('Save', self)
        self._save_action.setShortcut('Ctrl+S')
        self._save_action.triggered.connect(self.tabbed_editor.saveFile)
        self._save_action.setEnabled(False)

        self._save_as_action = QAction('Save As...', self)
        self._save_as_action.setShortcut('Ctrl+Shift+S')
        self._save_as_action.triggered.connect(self.tabbed_editor.saveAsFile)
        self._save_as_action.setEnabled(False)

        file_menu = self.menu_bar.addMenu('File')
        file_menu.addAction(newAction)
        file_menu.addAction(openAction)
        file_menu.addAction(self._save_action)
        file_menu.addAction(self._save_as_action)

    def disableSave(self):
        self._save_action.setEnabled(False)
        self._save_as_action.setEnabled(False)

    def enableSave(self):
        self._save_action.setEnabled(True)
        self._save_as_action.setEnabled(True)


class TabbedEditor(QTabWidget):
    def __init__(self, parent=None, *args, **kwargs):
        QWidget.__init__(self, parent, *args, **kwargs)
        self.unsaved_tabs = []
        self.file_dialog = QFileDialog()
        self.file_dialog.setFileMode(QFileDialog.AnyFile)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)

    def closeTab(self, idx):
        editor = self.widget(idx)
        if editor in self.unsaved_tabs:
            msg_box = QMessageBox()
            ret = msg_box.warning(self, 'Closing an unsaved file!', 'Are you sure you want to close this tab?',
                                  QMessageBox.Ok, QMessageBox.Cancel)
            if ret == QMessageBox.Ok:
                self.removeTab(idx)
        else:
            self.removeTab(idx)

        if self.count() == 0:
            parent = self.parent()
            if isinstance(parent, CodeEditorWidget):
                parent.disableSave()

    def saveBreakpoints(self):
        idx = self.currentIndex()
        editor = self.widget(idx)

        bpl.set_breakpoints(str(editor.file_path), editor.breakpoints)
        bpl.save()

    def saveAsFile(self):
        idx = self.currentIndex()
        editor = self.widget(idx)
        content = editor.toPlainText()

        file_path = self.file_dialog.getSaveFileName(self, 'Save File As')

        if len(file_path) > 0:
            f = open(file_path, 'w')
            with f:
                f.write(content)

            self.saveBreakpoints()

        if editor in self.unsaved_tabs:
            self.setTabText(idx, editor.file_path)
            self.unsaved_tabs.remove(editor)

    def saveFile(self):
        idx = self.currentIndex()
        editor = self.widget(idx)
        file_path = editor.file_path
        content = editor.toPlainText()

        if file_path is None or not os.path.isfile(file_path):
            file_path = self.file_dialog.getSaveFileName(self, 'Save File As')

        if len(file_path) > 0:
            f = open(file_path, 'w')
            with f:
                f.write(content)

            self.saveBreakpoints()

        if editor in self.unsaved_tabs:
            self.setTabText(idx, editor.file_path)
            self.unsaved_tabs.remove(editor)

    def newFile(self):
        self.addFileTab('new', True)

    def openFile(self, file_name=None):
        print 'Before: ' + str(file_name)
        if file_name is None:
            file_name = self.file_dialog.getOpenFileName(self, 'Open File')
        print 'After: ' + str(file_name)
        if len(file_name) > 0 and not self.isFileOpened(file_name):
            idx = self.addFileTab(file_name)
            self.setCurrentIndex(idx)

    def isFileOpened(self, file_name):
        for i in range(self.count()):
            tab = self.widget(i)
            if tab.file_path == file_name:
                return True
        return False

    def addUnsavedTab(self, tab):
        idx = self.indexOf(tab)
        if tab not in self.unsaved_tabs:
            self.unsaved_tabs.append(tab)

        if tab.file_path is not None:
            self.setTabText(idx, str(tab.file_path) + '*')

    def addFileTab(self, file_name, is_new=False):
        tab = BreakpointsEditor(self)
        idx = self.addTab(tab, file_name)

        if not is_new:
            tab.openFile(file_name)
        tab.textChanged.connect(lambda: self.addUnsavedTab(tab))

        parent = self.parent()
        if isinstance(parent, CodeEditorWidget):
            parent.enableSave()

        return idx


class DebugWidget(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.setLayout(QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)

        self.continueAction = None
        self.pauseAction = None
        self.stopAction = None

        self.tb = self._createToolbar()

        self.layout().addWidget(self.tb)

        self.editor = DebugEditor()
        self.layout().addWidget(self.editor)

        self.setEnabled(False)

        dispatcher.connect(self.enable, signal=signals.SetupDebugger)
        dispatcher.connect(lambda: [self.enableButtons(), self.pauseAction.setEnabled(False)],
                           signal=signals.PauseDebugger)
        dispatcher.connect(self.disable, signal=signals.EndDebugger)

    def enableButtons(self, *args, **kwargs):
        for action in self.tb.actions():
            action.setEnabled(True)

    def enable(self, *args, **kwargs):
        self.setEnabled(True)

    def disable(self, *args, **kwargs):
        self.setEnabled(False)
        self.disableButtons()
        self.editor.clear()

    def disableButtons(self):
        for action in self.tb.actions():
            action.setEnabled(False)

    def _preContinue(self):
        self.disableButtons()
        self.pauseAction.setEnabled(True)
        self.stopAction.setEnabled(True)

    def resumeDebugger(self):
        self._preContinue()
        debugger.resume()

    def stopDebugger(self):
        debugger.stop()

    def killDebugger(self):
        debugger.kill()

    def stepOver(self):
        self._preContinue()
        debugger.step_over()

    def stepInto(self):
        self._preContinue()
        debugger.step_into()

    def stepOut(self):
        self._preContinue()
        debugger.step_out()

    def stepInstruction(self):
        self._preContinue()
        debugger.step_instruction()

    def stepOutOfFrame(self):
        self._preContinue()
        debugger.step_out_of_frame()

    def _createToolbar(self):
        tb = QToolBar()
        self.continueAction = QAction(QIcon(resource_path('play.svg')), 'Continue', self)
        self.continueAction.triggered.connect(self.resumeDebugger)
        self.continueAction.setEnabled(False)

        self.pauseAction = QAction(QIcon(resource_path('pause.svg')), 'Pause', self)
        self.pauseAction.triggered.connect(self.stopDebugger)
        self.pauseAction.setEnabled(False)

        self.stopAction = QAction(QIcon(resource_path('stop.svg')), 'Stop', self)
        self.stopAction.triggered.connect(self.killDebugger)
        self.stopAction.setEnabled(False)

        step_over = QAction(QIcon(resource_path('step_over.ico')), 'Step Over', self)
        step_over.triggered.connect(self.stepOver)
        step_over.setEnabled(False)

        step_into = QAction(QIcon(resource_path('step_into.ico')), 'Step Into', self)
        step_into.triggered.connect(self.stepInto)
        step_into.setEnabled(False)

        step_out = QAction(QIcon(resource_path('step_out.ico')), 'Step Out', self)
        step_out.triggered.connect(self.stepOut)
        step_out.setEnabled(False)

        step_instruction = QAction(QIcon(resource_path('step_instruction.ico')), 'Step Single Instruction', self)
        step_instruction.triggered.connect(self.stepInstruction)
        step_instruction.setEnabled(False)

        step_out_of_frame = QAction(QIcon(resource_path('step_out_of_frame.ico')), 'Step Out Of Frame', self)
        step_out_of_frame.triggered.connect(self.stepOutOfFrame)
        step_out_of_frame.setEnabled(False)

        tb.addActions([self.continueAction, self.pauseAction, self.stopAction])
        tb.addSeparator()
        tb.addActions([step_over, step_into, step_out, step_out_of_frame, step_instruction])
        return tb


class DebugEditor(Editor):
    def __init__(self, *args):
        Editor.__init__(self, *args)

        self.setReadOnly(True)

        dispatcher.connect(self.updateFile, signal=signals.PauseDebugger)

    def updateFile(self, *args, **kwargs):
        cur_file = debugger.get_selected_frame_file()
        if cur_file is not None:
            if self.file_path is None or self.file_path != cur_file:
                self.openFile(cur_file)
                self.file_path = cur_file
            self.updateLine(args, kwargs)

    def updateLine(self, *args, **kwargs):
        cur_frame = debugger.get_selected_frame()
        line = cur_frame.GetLineEntry().GetLine()
        self.scrollToLine(line)

    def mousePressEvent(self, QMouseEvent):
        # disable mouse presses
        pass

    @property
    def breakpoints(self):
        bps = debugger.get_breakpoints(self.file_path)
        res = []
        for bp in bps:
            line = bp.GetLocationAtIndex(0).GetAddress().GetLineEntry().GetLine()
            res.append(line - 1)
        return res

    def lineNumberAreaMousePressEvent(self, QMouseEvent):
        pass

    def lineNumberAreaPaintEvent(self, QPaintEvent):
        painter = QPainter(self.line_number_area)
        bg_color = constants.LINE_NUMBER_AREA_BACKGROUND_COLOR
        painter.fillRect(QPaintEvent.rect(), bg_color)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        height = self.fontMetrics().height()
        while block.isValid() and (top <= QPaintEvent.rect().bottom()):
            if block.isVisible() and (bottom >= QPaintEvent.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(constants.LINE_NUMBER_AREA_FONT_COLOR)
                painter.drawText(0, top, self.line_number_area.width(), height, Qt.AlignRight, number)
                if blockNumber in self.breakpoints:
                    painter.setBrush(Qt.red)
                    painter.drawEllipse(0, top + height / 8, 3 * height / 4, 3 * height / 4)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
