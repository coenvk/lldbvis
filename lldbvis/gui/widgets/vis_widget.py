import threading

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *

from lldbvis.events import signals
from lldbvis.events import dispatcher
from lldbvis.events import Input
from lldbvis.tree import *
from lldbvis.util.camera import Camera
from lldbvis.settings import constants
from lldbvis.tree.layouts import TopDownCircularLayout

try:
    del debugger
except NameError:
    pass
finally:
    from lldbvis.debug import debugger


class VisWidget(QGLWidget):
    def __init__(self, parent=None):
        super(VisWidget, self).__init__(parent)
        self.layout = TopDownCircularLayout(1.0)
        self.camera = Camera()
        self.setMouseTracking(True)
        self.quadric = gluNewQuadric()
        self.input = Input(self.camera)
        self.root = None
        self._selectedId = 0

        self.timer = QBasicTimer()
        self.timedUpdate()

        dispatcher.connect(self.updateWidget, signal=signals.PauseDebugger)
        dispatcher.connect(self.timedUpdate, signal=signals.EndDebugger)

    def timedUpdate(self, interval=constants.DEFAULT_OPENGL_TIMED_UPDATE_INTERVAL_MS, restart=False):
        if not self.timer.isActive():
            self.timer.start(interval, self)
        elif restart:
            self.timer.stop()
            self.timer.start(interval, self)

    def _addChildValues(self, node, value):
        if value.IsValid():
            child_values = debugger.value_children(value)

            for child_value in child_values:
                child_node = Node(data=NodeDataFactory(child_value))
                node.add(child_node)

                self._addChildValues(child_node, child_value)

    def updateWidget(self, *args, **kwargs):
        if self.root is None:
            self.root = Node(data=NodeDataFactory(debugger.process))

        self.selectedId = 0

        with threading.Lock():
            self.root.clear()
            self.root.data.setTo(debugger.process)

            for thread in debugger.threads():
                t_node = Node(data=NodeDataFactory(thread))
                self.root.add(t_node)

                for frame in debugger.frames(thread):
                    f_node = Node(data=NodeDataFactory(frame))
                    t_node.add(f_node)

                    for value in debugger.values(frame, thread):
                        v_node = Node(data=NodeDataFactory(value))
                        f_node.add(v_node)

                        self._addChildValues(v_node, value)

            self.layout.apply(self.root)

    @property
    def selectedId(self):
        return self._selectedId

    @selectedId.setter
    @dispatcher.send(signal=signals.SelectNode)
    def selectedId(self, id):
        self._selectedId = id

    def initializeGL(self):
        clear_color = constants.OPENGL_BACKGROUND_COLOR
        glClearColor(clear_color.redF(), clear_color.greenF(), clear_color.blueF(), clear_color.alphaF())

        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)

        glEnable(GL_POLYGON_SMOOTH)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_CULL_FACE)
        glShadeModel(GL_SMOOTH)

        glEnable(GL_MULTISAMPLE)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

        global_ambient = constants.OPENGL_GLOBAL_LIGHT_AMBIENT
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, global_ambient)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, 1)

        light0 = constants.OPENGL_LIGHT0

        glLightfv(GL_LIGHT0, GL_POSITION, light0.position.asArray())
        glLightfv(GL_LIGHT0, GL_AMBIENT, light0.ambient.asArray())
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light0.diffuse.asArray())
        glLightfv(GL_LIGHT0, GL_SPECULAR, light0.specular.asArray())

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        glColorMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)

        gluQuadricNormals(self.quadric, GLU_SMOOTH)

        self.setFocusPolicy(Qt.StrongFocus)
        self.format().setDoubleBuffer(True)
        self.setAutoBufferSwap(True)
        self.format().setDepth(True)

    def timerEvent(self, QTimerEvent):
        self.update()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self.root is not None and debugger.running:
            glLoadIdentity()

            glTranslatef(-self.camera.x, -self.camera.y, -self.camera.z)
            glRotatef(self.camera.eulerAngleZDeg, 0, 0, 1)
            glRotatef(self.camera.eulerAngleYDeg, 0, 1, 0)
            glRotatef(self.camera.eulerAngleXDeg, 1, 0, 0)

            sel_node = self.selectedNode()
            glTranslatef(-sel_node.absoluteX, -sel_node.absoluteY, -sel_node.absoluteZ)

            glPushMatrix()

            self.root.draw(self)

            glPopMatrix()

            glFlush()
            self.timedUpdate(restart=True)

        else:
            self._drawCenteredText('Set a target and run the debugger')
            glFlush()
            self.timedUpdate(100, True)

    def _drawCenteredText(self, text):
        painter = QPainter(self)
        rect = QRectF(0, 0, self.width(), self.height())
        painter.setPen(constants.OPENGL_FONT_COLOR)
        painter.setFont(constants.OPENGL_FONT)
        text_options = QTextOption(Qt.AlignCenter)
        text_options.setWrapMode(QTextOption.WordWrap)
        painter.drawText(rect, text, text_options)

    def selectedNode(self):
        return self.root.getById(self.selectedId)

    def close(self):
        QGLWidget.close(self)
        gluDeleteQuadric(self.quadric)

    def resizeGL(self, width, height):
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.projection(width, height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def keyPressEvent(self, QKeyEvent):
        if debugger.running:
            self.input.key_press(QKeyEvent)

    def mousePressEvent(self, QMouseEvent):
        self.input.mouse_press(QMouseEvent)

    def mouseReleaseEvent(self, QMouseEvent):
        if self.input.leftPressed and not self.input.mouseDrag:
            self.select(QMouseEvent.x(), QMouseEvent.y())
        self.input.mouse_release(QMouseEvent)

    def projection(self, width, height):
        return gluPerspective(constants.OPENGL_PERSPECTIVE_FOVY, float(width) / float(height),
                              constants.OPENGL_PERSPECTIVE_NEAR, constants.OPENGL_PERSPECTIVE_FAR)

    def select(self, x, y):
        viewport = glGetIntegerv(GL_VIEWPORT)
        glSelectBuffer(512)
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(0)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPickMatrix(x, self.height() - y, 4, 4, viewport)
        self.projection(viewport[2] - viewport[0], viewport[3] - viewport[1])
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.repaint()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        selection_buffer = glRenderMode(GL_RENDER)
        if len(selection_buffer) > 0:
            choice = selection_buffer[0].names[0]
            depth = selection_buffer[0].near
            for i in range(1, len(selection_buffer)):
                if selection_buffer[i].near < depth:
                    choice = selection_buffer[i].names[0]
                    depth = selection_buffer[i].near
            if self.root.getById(choice) is not None:
                self.selectedId = choice

    def mouseMoveEvent(self, QMouseEvent):
        if debugger.running:
            self.input.mouse_move(QMouseEvent)

    def wheelEvent(self, QWheelEvent):
        if debugger.running:
            self.input.mouse_wheel(QWheelEvent)
            min_dist = self.selectedNode().geom.radius + 1
            if self.camera.position.z < min_dist:
                self.camera.position.z = min_dist
