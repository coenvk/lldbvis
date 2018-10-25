from math import *

from OpenGL.GL import *
from OpenGL.GLU import *

from Color import Color3
from Label import Label
from Material import Material
from Vector import Vector4, Vector3


class NodeGeometry:
    def __init__(self, node):
        self.position = Vector3()
        self.radius = 0.2
        self.child_distance = 0
        self.color = Color3.red()
        self.material = Material(
            Vector4(0, 0, 0.025, 1),
            Vector4(0.4, 0.4, 0.45, 1),
            Vector4(0.04, 0.04, 0.37, 1),
            Vector4(0, 0, 0, 1),
            0.078125)
        self.collapsed = False
        self.node = node
        self.label = Label(self.node, Vector3(self.x, self.y, self.z))

    @property
    def absolutePosition(self):
        pos = self.position.__copy__()
        if not self.node.isRoot():
            pos += self.node.parent.geom.absolutePosition
        return pos

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    @property
    def z(self):
        return self.position.z

    @property
    def absoluteX(self):
        return self.absolutePosition.x

    @property
    def absoluteY(self):
        return self.absolutePosition.y

    @property
    def absoluteZ(self):
        return self.absolutePosition.z

    def toggleCollapsed(self):
        self.collapsed = not self.collapsed

    def _preOutline(self):
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glEnable(GL_LIGHTING)
        glClearStencil(0)
        glClear(GL_STENCIL_BUFFER_BIT)
        glEnable(GL_STENCIL_TEST)
        glStencilFunc(GL_ALWAYS, 1, 0xffff)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def _postOutline(self, quadric):
        glDisable(GL_LIGHTING)
        glStencilFunc(GL_NOTEQUAL, 1, 0xffff)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
        glLineWidth(3.0)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(1, 1, 1)
        gluSphere(quadric, self.radius, 20, 20)
        glPopAttrib()

    def _drawCylinder(self, pos, radius, subdivisions, quadric):
        v1 = pos.__copy__()

        n1 = v1.unit()
        n2 = Vector3.unitZ()

        angle = acos(n1.dot(n2))

        if abs(angle) < 0.001:
            angle = 0

        axis = n1.cross(n2).unit()

        angle = angle * 180 / pi + 180

        glRotatef(angle, axis.x, axis.y, axis.z)

        gluQuadricOrientation(quadric, GLU_OUTSIDE)
        gluCylinder(quadric, radius, radius, v1.length(), subdivisions, 1)

    def draw(self, widget):
        quadric = widget.quadric
        highlight_id = widget.selectedId

        glPushMatrix()
        self.material.setGL()

        glTranslatef(self.x, self.y, self.z)

        if not self.collapsed:
            for i in range(self.node.size()):
                child = self.node[i]

                Material.chrome().setGL()

                glPushMatrix()

                self._drawCylinder(child.geom.position, 0.03, 5, quadric)

                glPopMatrix()

                child.draw(widget)

        # draw outline
        outlined = self.node.id == highlight_id
        if outlined:
            self._preOutline()
        glColor3f(self.color.r, self.color.g, self.color.b)
        glLoadName(self.node.id)
        gluSphere(quadric, self.radius, 20, 20)
        if outlined:
            self._postOutline(quadric)

        # draw label
        if widget.camera.distance(self.absolutePosition - widget.selectedNode().absolutePosition) < 8 or highlight_id == self.node.id:
            self.label.draw(widget)

        glPopMatrix()
