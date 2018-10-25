from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4.QtCore import *
from PyQt4.QtOpenGL import *
from PyQt4.QtGui import *

from Camera import Camera
from Input import Input
from Layout import *
from Light import Light
from Node import Node
from NodeData import *
from Vector import Vector4
from Observer import observable, Observer


class VisWidget(QGLWidget):
    def __init__(self, parent=None):
        super(VisWidget, self).__init__(parent)
        self.debugger = Debugger()
        self.layout = CircularLayout(0.4)
        self.camera = Camera()
        self.setMouseTracking(True)
        self.quadric = gluNewQuadric()
        self.input = Input(self.camera)
        self.root = None
        self._selectedId = 0

        Observer().add(self.debugger, 'pause', self.updateWidget)

    def updateWidget(self, *args, **kwargs):
        if self.root is None:
            self.root = Node(data=NodeDataFactory(self.debugger.process))

        self.root.clear()
        self.root.data.setTo(self.debugger.process)

        for thread in self.debugger.threads():
            t_node = Node(data=NodeDataFactory(thread))
            self.root.add(t_node)
            for frame in self.debugger.frames(thread):
                f_node = Node(data=NodeDataFactory(frame))
                t_node.add(f_node)
                for value in self.debugger.values(frame, thread):
                    v_node = Node(data=NodeDataFactory(value))
                    f_node.add(v_node)

        self.layout.apply(self.root)

    @property
    def selectedId(self):
        return self._selectedId

    @selectedId.setter
    @observable
    def selectedId(self, id):
        self._selectedId = id

    def initializeGL(self):
        glClearColor(0.118, 0.133, 0.142, 1)

        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POLYGON_SMOOTH)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_CULL_FACE)
        glShadeModel(GL_SMOOTH)

        glEnable(GL_MULTISAMPLE)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

        global_ambient = [0.4, 0.4, 0.4, 1.0]
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, global_ambient)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, 1)

        light0 = Light(
            Vector4(0, 50, 100, 0),
            Vector4(0, 0, 0, 1),
            Vector4(1, 1, 1, 1),
            Vector4(1, 1, 1, 1))

        glLightfv(GL_LIGHT0, GL_POSITION, light0.position.asArray())
        glLightfv(GL_LIGHT0, GL_AMBIENT, light0.ambient.asArray())
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light0.diffuse.asArray())
        glLightfv(GL_LIGHT0, GL_SPECULAR, light0.specular.asArray())

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        gluQuadricNormals(self.quadric, GLU_SMOOTH)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setAutoBufferSwap(True)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self.root is not None and self.debugger.isSetup:
            glLoadIdentity()

            glTranslatef(-self.camera.x, -self.camera.y, -self.camera.z)
            glRotatef(self.camera.eulerAngleZDeg, 0, 0, 1)
            glRotatef(self.camera.eulerAngleYDeg, 0, 1, 0)
            glRotatef(self.camera.eulerAngleXDeg, 1, 0, 0)

            selectedNode = self.selectedNode()
            glTranslatef(-selectedNode.absoluteX, -selectedNode.absoluteY, -selectedNode.absoluteZ)

            glPushMatrix()

            self.root.draw(self)

            glPopMatrix()

        else:
            self._drawCenteredText('Set a target and run the debugger')

        self.update()

    def _drawCenteredText(self, text):
        painter = QPainter(self)
        rect = QRectF(0, 0, self.width(), self.height())
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Arial', 16))
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
        self.input.key_press(QKeyEvent)

    def mousePressEvent(self, QMouseEvent):
        self.input.mouse_press(QMouseEvent)

    def mouseReleaseEvent(self, QMouseEvent):
        if self.input.leftPressed and not self.input.mouseDrag:
            self.select(QMouseEvent.x(), QMouseEvent.y())
        self.input.mouse_release(QMouseEvent)

    def projection(self, width, height):
        return gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)

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
            self.selectedId = choice

    def mouseMoveEvent(self, QMouseEvent):
        self.input.mouse_move(QMouseEvent)

    def wheelEvent(self, QWheelEvent):
        self.input.mouse_wheel(QWheelEvent)
