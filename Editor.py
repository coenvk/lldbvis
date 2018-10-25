from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Debugger import Debugger
from Observer import Observer
from lldb import *
import sys
import qdarkstyle
import os


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

        self.filePath = None

        self.lineNumberArea = LineNumberArea(self)

        self.connect(self, SIGNAL('blockCountChanged(int)'), self.updateLineNumberAreaWidth)
        self.connect(self, SIGNAL('updateRequest(QRect,int)'), self.updateLineNumberArea)
        self.connect(self, SIGNAL('cursorPositionChanged()'), self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)

    def scrollToLine(self, line):
        self.moveCursor(QTextCursor.End)
        cursor = QTextCursor(self.document().findBlockByLineNumber(line - 1))
        self.setTextCursor(cursor)

    def openFile(self, name):
        self.filePath = name
        file = open(name, 'r')
        with file:
            content = file.read()
            self.setPlainText(content)

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 20 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, QResizeEvent):
        QPlainTextEdit.resizeEvent(self, QResizeEvent)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

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
        painter = QPainter(self.lineNumberArea)
        bg_color = QColor(200, 200, 200, 70)
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
                painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []
        selection = QTextEdit.ExtraSelection()
        lineColor = QColor(255, 255, 255, 120).dark(255)

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        extraSelections.append(selection)

        self.setExtraSelections(extraSelections)


class CodeEditor(QMainWindow):
    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.tabbed_editor = TabbedEditor()
        self.setCentralWidget(self.tabbed_editor)
        self.menu_bar = self.menuBar()
        self.createFileMenu()
        self.resize(800, 600)

    def createFileMenu(self):
        newAction = QAction('New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.tabbed_editor.newFile)

        openAction = QAction('Open...', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.tabbed_editor.openFile)

        saveAction = QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.tabbed_editor.saveFile)

        saveAsAction = QAction('Save As...', self)
        saveAsAction.setShortcut('Ctrl+Shift+S')
        saveAsAction.triggered.connect(self.tabbed_editor.saveAsFile)

        file_menu = self.menu_bar.addMenu('File')
        file_menu.addAction(newAction)
        file_menu.addAction(openAction)
        file_menu.addAction(saveAction)
        file_menu.addAction(saveAsAction)


class TabbedEditor(QTabWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.unsaved_tabs = []
        self.file_dialog = QFileDialog()
        self.file_dialog.setFileMode(QFileDialog.AnyFile)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)

    def closeTab(self, idx):
        editor = self.widget(idx)
        if editor in self.unsaved_tabs:
            msg_box = QMessageBox()
            ret = msg_box.warning(self, 'Closing an unsaved file!', 'Are you sure you want to close this tab?', QMessageBox.Ok, QMessageBox.Cancel)
            if ret == QMessageBox.Ok:
                self.removeTab(idx)
        else:
            self.removeTab(idx)

    def saveAsFile(self):
        idx = self.currentIndex()
        editor = self.widget(idx)
        content = editor.toPlainText()

        file_path = self.file_dialog.getSaveFileName(self, 'Save File As')

        if len(file_path) > 0:
            f = open(file_path, 'w')
            with f:
                f.write(content)

        if editor in self.unsaved_tabs:
            self.setTabText(idx, editor.filePath)
            self.unsaved_tabs.remove(editor)

    def saveFile(self):
        idx = self.currentIndex()
        editor = self.widget(idx)
        file_path = editor.filePath
        content = editor.toPlainText()

        if file_path is None or not os.path.isfile(file_path):
            file_path = self.file_dialog.getSaveFileName(self, 'Save File As')

        if len(file_path) > 0:
            f = open(file_path, 'w')
            with f:
                f.write(content)

        if editor in self.unsaved_tabs:
            self.setTabText(idx, editor.filePath)
            self.unsaved_tabs.remove(editor)

    def newFile(self):
        self.addFileTab('new', True)

    def openFile(self):
        file_name = self.file_dialog.getOpenFileName(self, 'Open File')
        if len(file_name) > 0:
            idx = self.addFileTab(file_name)
            self.setCurrentIndex(idx)

    def addUnsavedTab(self, idx):
        tab = self.widget(idx)
        if tab not in self.unsaved_tabs:
            self.unsaved_tabs.append(tab)

        if tab.filePath is not None:
            self.setTabText(idx, str(tab.filePath) + '*')

    def addFileTab(self, file_name, is_new=False):
        tab = Editor()
        idx = self.addTab(tab, file_name)
        if not is_new:
            tab.openFile(file_name)
        tab.textChanged.connect(lambda: self.addUnsavedTab(idx))
        return idx


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt()
    app.setStyleSheet(dark_stylesheet)
    window = CodeEditor()
    window.show()
    sys.exit(app.exec_())


class DebugWidget(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.debugger = Debugger()

        self.setLayout(QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)

        self.tb = self.createToolbar()
        self.layout().addWidget(self.tb)

        editor = DebugEditor()
        self.layout().addWidget(editor)

        self.setEnabled(False)

        Observer().add(self.debugger, 'setup', self.enable)

    def enable(self, *args, **kwargs):
        self.setEnabled(True)

    def createToolbar(self):
        tb = QToolBar()
        continue_process = QAction(QIcon('icons/play.svg'), 'Continue', self)
        pause_process = QAction(QIcon('icons/pause.svg'), 'Pause', self)
        stop_process = QAction(QIcon('icons/stop.svg'), 'Stop', self)

        step_over = QAction(QIcon('icons/step_over.ico'), 'Step Over', self)
        step_into = QAction(QIcon('icons/step_into.ico'), 'Step Into', self)
        step_out = QAction(QIcon('icons/step_out.ico'), 'Step Out', self)
        step_instruction = QAction(QIcon('icons/step_instruction.ico'), 'Step Single Instruction', self)
        step_out_of_frame = QAction(QIcon('icons/step_out_of_frame.ico'), 'Step Out Of Frame', self)
        tb.addActions([continue_process, pause_process, stop_process])
        tb.addSeparator()
        tb.addActions([step_over, step_into, step_out, step_out_of_frame, step_instruction])
        return tb


class DebugEditor(Editor):
    def __init__(self, *args):
        Editor.__init__(self, *args)
        self.debugger = Debugger()

        self.setReadOnly(True)

        Observer().add(self.debugger, 'pause', self.updateFile)

    def updateFile(self, *args, **kwargs):
        cur_file = self.debugger.currentFrameFile
        if cur_file is not None:
            if self.filePath is None or self.filePath != cur_file:
                self.openFile(cur_file)
                self.filePath = cur_file
            self.updateLine(args, kwargs)

    def updateLine(self, *args, **kwargs):
        cur_frame = self.debugger.currentFrame
        line = cur_frame.GetLineEntry().GetLine()
        self.scrollToLine(line)

    def mousePressEvent(self, QMouseEvent):
        # disable mouse presses
        pass

    @property
    def breakpoints(self):
        bps = self.debugger.breakpoints(self.filePath)
        res = []
        for bp in bps:
            line = SBLineEntry(bp.GetLocationAtIndex(0).GetAddress().GetLineEntry()).GetLine()
            res.append(line - 1)
        return res

    def lineNumberAreaMousePressEvent(self, QMouseEvent):
        pass
        # state = self.debugger.process.GetState()
        # if not self.debugger.process.IsValid() or state == eStateStopped or state == eStateExited:
        #     block = self.firstVisibleBlock()
        #     blockNumber = block.blockNumber()
        #     top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        #     height = self.blockBoundingRect(block).height()
        #     width = self.lineNumberArea.width()
        #     bottom = top + height
        #     while block.isValid():
        #         if top <= QMouseEvent.y() <= bottom and 0 <= QMouseEvent.x() <= width:
        #             if blockNumber not in self.breakpoints:
        #                 self.debugger.addBreakpoint(self.filePath, blockNumber + 1)
        #             elif blockNumber in self.breakpoints:
        #                 bp = SBBreakpoint(self.debugger.breakpoints(self.filePath, blockNumber + 1)[0])
        #                 self.debugger.removeBreakpoint(bp)
        #
        #         block = block.next()
        #         top = bottom
        #         bottom = top + self.blockBoundingRect(block).height()
        #         blockNumber += 1
        #
        #     self.repaint()

    def lineNumberAreaPaintEvent(self, QPaintEvent):
        painter = QPainter(self.lineNumberArea)
        bg_color = QColor(200, 200, 200, 70)
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
                painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignRight, number)
                if blockNumber in self.breakpoints:
                    painter.setBrush(Qt.red)
                    painter.drawEllipse(0, top + height / 8, 3 * height / 4, 3 * height / 4)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
