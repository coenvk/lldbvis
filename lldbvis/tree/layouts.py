from math import *

from lldbvis.settings import constants
from lldbvis.util.vectors import Vector3


class Layout:
    def __init__(self, anchor=Vector3()):
        self.anchor = anchor

    def apply(self, root):
        raise NotImplementedError


class CircularLayout(Layout):
    def __init__(self, min_radius=constants.LAYOUT_MINIMAL_RADIUS, anchor=None):
        Layout.__init__(self, anchor)
        self.min_radius = min_radius

    def apply(self, root):
        if self.anchor is None:
            self.anchor = root.geom.position
        else:
            root.geom.position = self.anchor

        self.initializeNodeData(root)
        self.layoutRoot(root)

    def initializeNodeData(self, root):
        root_geom = root.geom
        if root_geom.child_distance < self.min_radius:
            root_geom.child_distance = self.min_radius

        for i in range(root.size()):
            child = root[i]
            self.initializeNodeData(child)

    def layoutRoot(self, root):
        if root.hasChildren():
            rot = -pi / 2

            self.pushAwayChildren(root)
            root_geom = root.geom
            radius = root_geom.radius + root_geom.child_distance

            drot = 2 * pi / root.size()
            for i in range(root.size()):
                child = root[i]
                child_geom = child.geom
                child_geom.position.x = cos(rot) * radius
                child_geom.position.y = sin(rot) * radius
                rot += drot
                self.pushAwayFromParent(child)
                self.layoutChildren(child)

    def layoutChildren(self, node):
        if node.hasChildren():
            self.pushAwayChildren(node)
            node_geom = node.geom
            opposite_vector = -node_geom.position.unit()

            rot = opposite_vector.angle()
            if opposite_vector.y < 0:
                rot = 2 * pi - rot

            radius = node_geom.radius + node_geom.child_distance

            drot = 2 * pi / (node.size() + 1)
            rot += drot

            for i in range(node.size()):
                child = node[i]
                child_geom = child.geom
                child_geom.position.x = cos(rot) * radius
                child_geom.position.y = sin(rot) * radius
                rot += drot
                self.pushAwayFromParent(child)
                self.layoutChildren(child)

    def pushAwayChildren(self, node):
        if node.hasChildren():
            node_geom = node.geom
            circ = (node_geom.child_distance + node_geom.radius) * 2 * pi
            node_diameter_sum = 0

            if not node.isRoot():
                node_diameter_sum += (node.parent.geom.radius * 2)

            for i in range(node.size()):
                child = node.getByIndex(i)
                node_diameter_sum += (child.geom.radius * 2)

            node_diameter_sum *= constants.LAYOUT_DIAMETER_MULTIPLIER
            if circ < node_diameter_sum:
                r = node_diameter_sum / (2 * pi)
                node_geom.child_distance = r - node_geom.radius

    def pushAwayFromParent(self, node):
        if node.isRoot():
            return

        if node.hasChildren():
            node_geom = node.geom
            distance = node.parent.geom.child_distance + (
                    node.size() * constants.LAYOUT_PUSH_DIRECT_CHILDREN_FACTOR + node.totalSize() * (
                    node.parent.size() * constants.LAYOUT_PUSH_PARENT_DIRECT_CHILDREN_FACTOR +
                    constants.LAYOUT_PUSH_CHILDREN_FACTOR)) * constants.LAYOUT_PUSH_FORCE
            pos_unit = node_geom.position.unit()
            node_geom.position = pos_unit * distance


class TopDownCircularLayout(CircularLayout):
    def __init__(self, min_distance=2, anchor=None):
        CircularLayout.__init__(self, min_distance, anchor)

    def layoutRoot(self, root):
        if root.hasChildren():
            self.pushAwayChildren(root)

            root_geom = root.geom
            radius = root_geom.radius + root_geom.child_distance

            if root.size() < 2:

                child = root[0]
                fst_child_geom = child.geom

                fst_child_geom.position.x = 0
                fst_child_geom.position.z = 0
                fst_child_geom.position.y = -radius

                self.pushAwayFromParent(child)
                self.layoutChildren(child)

            else:
                rot = pi / 2
                drot = 2 * pi / root.size()
                half_sqrt2 = sqrt(2) / 2

                for i in range(root.size()):
                    child = root[i]
                    child_geom = child.geom

                    child_geom.position.x = cos(rot)
                    child_geom.position.z = sin(rot)
                    child_geom.position.y = -1
                    child_geom.position *= half_sqrt2 * radius

                    rot += drot
                    self.pushAwayFromParent(child)
                    self.layoutChildren(child)

    def layoutChildren(self, node):
        if node.hasChildren():
            self.pushAwayChildren(node)
            node_geom = node.geom
            radius = node_geom.radius + node_geom.child_distance

            opposite_vector = node_geom.position.__copy__()
            opposite_vector.y = 0
            opposite_vector = -opposite_vector.unit()

            if opposite_vector.rounded(threshold=1e-6) == Vector3.zero():
                drot = 2 * pi / node.size()
                rot = pi / 2

            else:
                rot = opposite_vector.angle()
                if node_geom.position.z > 0:
                    rot = 2 * pi - rot

                drot = 2 * pi / (node.size() + 1)
                rot += drot

            half_sqrt2 = sqrt(2) / 2

            for i in range(node.size()):
                child = node[i]
                child_geom = child.geom
                child_geom.position.x = cos(rot)
                child_geom.position.z = sin(rot)
                child_geom.position.y = -1
                child_geom.position.scale(half_sqrt2 * radius)
                rot += drot
                self.pushAwayFromParent(child)
                self.layoutChildren(child)


class SphericalLayout(CircularLayout):
    def __init__(self, min_distance=2, anchor=None):
        CircularLayout.__init__(self, min_distance, anchor)
        self.slices = 2

    def layoutRoot(self, root):
        if root.hasChildren():
            self.pushAwayChildren(root)
            root_geom = root.geom
            radius = root_geom.radius + root_geom.child_distance

            slice_size = int(ceil(float(root.size()) / float(self.slices)))

            yrot = 0
            dyrot = pi / self.slices

            for j in range(self.slices):
                rot = - pi / 2

                drot = 2 * pi / slice_size
                for i in range(slice_size):
                    p = i + j * slice_size
                    if p >= root.size():
                        return
                    child = root[p]
                    child_geom = child.geom
                    child_geom.position.x = cos(rot) * radius
                    child_geom.position.y = sin(rot) * radius
                    child_geom.position.rotate3(0, yrot, 0)
                    rot += drot
                    self.pushAwayFromParent(child)
                    self.layoutChildren(child)

                yrot += dyrot

    def layoutChildren(self, node):
        if node.hasChildren():
            node_geom = node.geom
            opposite_vector = -node_geom.position.unit()

            self.pushAwayChildren(node)
            radius = node_geom.radius + node_geom.child_distance

            slice_size = int(ceil(float(node.size()) / float(self.slices)))

            yrot = 0
            dyrot = pi / self.slices

            for j in range(self.slices):

                if opposite_vector.y >= 0:
                    rot = opposite_vector.angle()
                else:
                    rot = 2 * pi - opposite_vector.angle()

                drot = 2 * pi / (slice_size + 1)
                rot += drot
                for i in range(slice_size):
                    p = i + j * slice_size
                    if p >= node.size():
                        return
                    child = node[p]
                    child_geom = child.geom
                    child_geom.position.x = cos(rot) * radius
                    child_geom.position.y = sin(rot) * radius
                    child_geom.position.rotate3(0, yrot, 0)
                    rot += drot
                    self.pushAwayFromParent(child)
                    self.layoutChildren(child)

                yrot += dyrot


class RectangularLayout(CircularLayout):
    def __init__(self, min_radius=2, anchor=None):
        CircularLayout.__init__(self, min_radius, anchor)
        self.min_radius = min_radius

    def apply(self, root):
        CircularLayout.apply(self, root)
        self.squareOut(root)

    def squareOut(self, node):
        if node.hasChildren():

            for i in range(node.size()):
                child = node[i]
                child_geom = child.geom

                pos_unit = child_geom.position.__copy__()
                pos_unit = pos_unit.unit()

                u = pos_unit.x
                v = pos_unit.y

                r = child_geom.position.length()

                u2 = pow(u, 2)
                v2 = pow(v, 2)

                sqrt2x2 = 2.0 * sqrt(2.0)

                subparam = 2.0 + u2 - v2
                paramx1 = subparam + u * sqrt2x2
                paramx2 = subparam - u * sqrt2x2

                subparam = 2.0 - u2 + v2
                paramy1 = subparam + v * sqrt2x2
                paramy2 = subparam - v * sqrt2x2

                epsilon = 0.0000001
                if fabs(paramx2) < epsilon:
                    paramx2 = 0.0
                if fabs(paramy2) < epsilon:
                    paramy2 = 0.0

                x = (sqrt(paramx1) - sqrt(paramx2)) / 2.0
                y = (sqrt(paramy1) - sqrt(paramy2)) / 2.0

                child_geom.position.x = x * r
                child_geom.position.y = y * r

                self.squareOut(child)


class BoxLayout(RectangularLayout):
    def __init__(self):
        RectangularLayout.__init__(self)
