import os
import sys
import warnings

try:
    import qdarkstyle
except:
    has_dark_style = False
else:
    has_dark_style = True

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from lldbvis.gui.windows import VisWindow
from lldbvis.gui.widgets import *


def main():
    os.environ['QT_API'] = 'pyqt'

    app = QApplication(sys.argv)

    if has_dark_style:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', FutureWarning)
            dark_stylesheet = qdarkstyle.load_stylesheet_from_environment()

        app.setStyleSheet(dark_stylesheet)

    window = VisWindow()

    widget = VisWidget()
    widget.resize(800, 600)

    editor = DebugWidget()
    frame_widget = FramesWidget()
    variable_widget = VariableWidget(widget)
    command_widget = CommandWidget()
    console_widget = ConsoleWidget()

    window.setCentralWidget(widget)

    bottom_dock_widget3 = QDockWidget(window)
    bottom_dock_widget3.setFeatures(QDockWidget.DockWidgetMovable)
    bottom_dock_widget3.setWidget(console_widget)
    bottom_dock_widget3.setWindowTitle("Console")

    bottom_dock_widget2 = QDockWidget(window)
    bottom_dock_widget2.setFeatures(QDockWidget.DockWidgetMovable)
    bottom_dock_widget2.setWidget(command_widget)
    bottom_dock_widget2.setWindowTitle("Commands Interpreter")

    bottom_dock_widget = QDockWidget(window)
    bottom_dock_widget.setFeatures(QDockWidget.DockWidgetMovable)
    bottom_dock_widget.setWidget(editor)
    bottom_dock_widget.setWindowTitle("Execution")

    left_dock_widget = QDockWidget(window)
    left_dock_widget.setFeatures(QDockWidget.DockWidgetMovable)
    left_dock_widget.setWidget(frame_widget)
    left_dock_widget.setWindowTitle("Frames")

    right_dock_widget = QDockWidget(window)
    right_dock_widget.setFeatures(QDockWidget.DockWidgetMovable)
    right_dock_widget.setWidget(variable_widget)
    right_dock_widget.setWindowTitle("Variables")

    window.addDockWidget(Qt.BottomDockWidgetArea, bottom_dock_widget)
    window.tabifyDockWidget(bottom_dock_widget, bottom_dock_widget2)
    window.addDockWidget(Qt.BottomDockWidgetArea, bottom_dock_widget3)
    bottom_dock_widget.show()
    bottom_dock_widget.raise_()

    window.addDockWidget(Qt.LeftDockWidgetArea, left_dock_widget)

    window.addDockWidget(Qt.RightDockWidgetArea, right_dock_widget)

    window.resize(widget.size())
    window.setWindowTitle('LLDBVis')

    window.show()

    exit_code = app.exec_()
    sys.exit(exit_code)


__all__ = ['main']
