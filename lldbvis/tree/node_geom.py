from math import *

from OpenGL.GL import *
from OpenGL.GLU import *

from lldbvis.settings import constants
from lldbvis.settings import *
from lldbvis.tree.label import Label
from lldbvis.util.material import Material
from lldbvis.util.vectors import Vector3


class NodeGeometry:
    def __init__(self, node, radius=constants.DEFAULT_OPENGL_NODE_RADIUS):
        self.position = Vector3()
        self.radius = radius
        self.child_distance = 0

        self.acceleration = Vector3()
        self.velocity = Vector3()

        self.material = constants.OPENGL_NODE_MATERIAL

        self.collapsed = False
        self.node = node
        self.label = Label(self.node, Vector3(self.x, self.y, self.z))

    @property
    def color(self):
        if self.node.isProcessNode():
            return ColorScheme.PROCESS_NODE.value
        elif self.node.isThreadNode():
            return ColorScheme.THREAD_NODE.value
        elif self.node.isFrameNode():
            return ColorScheme.FRAME_NODE.value
        elif self.node.isValueNode():
            return ColorScheme.VALUE_NODE.value

        return ColorScheme.DEFAULT.value

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
        gluSphere(quadric, self.radius, constants.OPENGL_NODE_SPHERE_SLICES, constants.OPENGL_NODE_SPHERE_STACKS)
        glPopAttrib()

    def _drawCylinder(self, pos, radius, subdivisions, quadric):
        v1 = pos.__copy__()

        n1 = v1.unit()
        n2 = Vector3.unitZ()

        angle = n1.angle(n2)

        if abs(angle) < 0.001:
            angle = 0

        axis = -n1.cross(n2).unit()

        angle = angle * 180 / pi

        glRotatef(angle, axis.x, axis.y, axis.z)

        gluQuadricOrientation(quadric, GLU_OUTSIDE)
        gluCylinder(quadric, radius, radius, v1.length(), subdivisions, 1)

    def draw(self, widget):
        quadric = widget.quadric
        highlight_id = widget.selectedId

        glEnable(GL_DEPTH_TEST)

        glPushMatrix()

        glTranslatef(self.x, self.y, self.z)

        if not self.collapsed:
            for i in range(self.node.size()):
                child = self.node[i]

                glPushAttrib(GL_ALL_ATTRIB_BITS)
                glPushMatrix()

                glDisable(GL_COLOR_MATERIAL)
                Material.chrome().setGL()

                self._drawCylinder(child.geom.position, constants.OPENGL_EDGE_CYLINDER_RADIUS,
                                   constants.OPENGL_EDGE_CYLINDER_SUBDIVISIONS, quadric)

                glPopMatrix()
                glPopAttrib()

                child.draw(widget)

        # draw outline
        outlined = self.node.id == highlight_id
        if outlined:
            self._preOutline()

        self.material.setGL()
        glColor3f(self.color.r, self.color.g, self.color.b)
        glLoadName(self.node.id)
        gluSphere(quadric, self.radius, constants.OPENGL_NODE_SPHERE_SLICES, constants.OPENGL_NODE_SPHERE_STACKS)
        if outlined:
            self._postOutline(quadric)

        # draw label
        if widget.camera.distance(
                self.absolutePosition - widget.selectedNode().absolutePosition) < \
                constants.OPENGL_MINIMAL_LABEL_ZOOM_DISTANCE or highlight_id == self.node.id:
            self.label.draw(widget)

        glPopMatrix()
