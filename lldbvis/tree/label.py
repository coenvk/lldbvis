from OpenGL.GL import *
from PyQt4.QtGui import *

from lldbvis.util.vectors import Vector3
from lldbvis.settings import constants


class Label:
    def __init__(self, node, position=Vector3()):
        self.node = node
        self.font = constants.OPENGL_LABEL_FONT
        self.fontMetrics = QFontMetrics(self.font)
        self.position = self.centerText(position)

    @property
    def text(self):
        if self.node.name is None:
            return ''
        return self.node.name

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    @property
    def z(self):
        return self.position.z

    def centerText(self, position):
        # TODO
        return position

    def draw(self, widget):
        glPushAttrib(GL_LIGHTING)
        glDisable(GL_LIGHTING)
        color = constants.OPENGL_LABEL_FONT_COLOR
        glColor3f(color.redF(), color.greenF(), color.blueF())
        glColor3f(1, 1, 1)
        widget.renderText(self.x, self.y, self.z, self.text, self.font)
        glPopAttrib()
