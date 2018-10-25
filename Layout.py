from Vector import Vector3
from math import *
import random
import sys


PUSH_FORCE = 0.3


class Layout:
    def __init__(self, anchor=Vector3()):
        self.anchor = anchor

    def apply(self, root):
        raise NotImplementedError


class CircularLayout(Layout):
    def __init__(self, min_radius=2, anchor=Vector3()):
        Layout.__init__(self, anchor)
        self.min_radius = min_radius

    def apply(self, root):
        if self.anchor is None:
            self.anchor = root.position
        else:
            root.position = self.anchor

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
            rot = 0

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
            node_geom = node.geom
            opposite_vector = -node_geom.position.unit()

            if opposite_vector.y >= 0:
                rot = opposite_vector.angle()
            else:
                rot = 2 * pi - opposite_vector.angle()

            self.pushAwayChildren(node)
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

            node_diameter_sum *= 1.1
            if circ < node_diameter_sum:
                r = node_diameter_sum / (2 * pi)
                node_geom.child_distance = r - node_geom.radius

    def pushAwayFromParent(self, node):
        if node.isRoot():
            return

        global PUSH_FORCE
        if node.hasChildren():
            node_geom = node.geom
            distance = node.parent.geom.child_distance + node.size() * PUSH_FORCE
            pos_unit = node_geom.position.unit()
            node_geom.position = pos_unit * distance


class ForceDirectedLayout(Layout):
    def __init__(self, anchor=Vector3()):
        Layout.__init__(self, anchor)
        random.seed(127396)

    def apply(self, root):
        self.initialize(root)
        # TODO: implement

    def initialize(self, root):
        root.position.x = random.randint(-50, 50)
        root.position.y = random.randint(-50, 50)
        root.position.z = random.randint(-50, 50)
        for i in range(root.size()):
            child = root[i]
            self.initialize(child)

    def calcBounds(self, root, bounds):
        if root.x < bounds[0]:
            bounds[0] = root.x
        if root.x > bounds[1]:
            bounds[1] = root.x
        if root.y < bounds[2]:
            bounds[2] = root.y
        if root.y > bounds[3]:
            bounds[3] = root.y
        if root.z < bounds[4]:
            bounds[4] = root.z
        if root.z > bounds[5]:
            bounds[5] = root.z
        for i in range(root.size()):
            bounds = self.calcBounds(root[i], bounds)
        return bounds

    def max(self, a, b, c):
        res = b if a < b else a
        res = c if res < c else res
        return res

    def scaleIt(self, root, factor):
        root.position *= (15 / factor)
        for i in range(root.size()):
            self.scaleIt(root[i], factor)

    def doScale(self, root):
        bounds = [sys.maxint, -sys.maxint - 1, sys.maxint, -sys.maxint - 1, sys.maxint, -sys.maxint - 1]
        bounds = self.calcBounds(root, bounds)
        dx = bounds[1] - bounds[0]
        dy = bounds[3] - bounds[2]
        dz = bounds[5] - bounds[4]
        factor = self.max(dx, dy, dz)
        self.scaleIt(root, factor)


class BalloonTreeLayout(Layout):
    def __init__(self, min_radius=2):
        Layout.__init__(self)
        self.min_radius = min_radius

    def apply(self, root):
        self.anchor = root.position
        self.firstWalk(root)
        self.secondWalk(root, None, self.anchor.x, self.anchor.y, 1, 0)

    def firstWalk(self, root):
        np = root.getParams()
        np.d = 0
        s = 0

        for i in range(root.size()):
            c = root.getByIndex(i)
            if c.display:
                self.firstWalk(c)
                cp = c.getParams()
                np.d = max(np.d, cp.r)
                cp.a = atan(float(cp.r) / float(np.d + cp.r))
                s += cp.a

        self.adjustChildren(np, s)
        np.r = max(np.d, self.min_radius) + 2 * np.d

    def adjustChildren(self, np, s):
        if s > pi:
            np.c = pi / s
            np.f = 0
        else:
            np.c = 1
            np.f = pi - s

    def secondWalk(self, n, r, x, y, l, t):
        n.x = x
        n.y = y
        np = n.getParams()
        num_children = 0

        for i in range(n.size()):
            c = n.getByIndex(i)
            if c.display:
                num_children += 1

        dd = l * np.d
        p = t + pi
        if num_children == 0:
            fs = 0
        else:
            fs = np.f / num_children
        pr = 0
        for i in range(n.size()):
            c = n.getByIndex(i)
            if c.display:
                cp = c.getParams()
                aa = np.c * cp.a
                rr = np.d * tan(aa) / (1 - tan(aa))
                p += pr + aa + fs
                xx = (l * rr + dd) * cos(p)
                yy = (l * rr + dd) * sin(p)
                pr = aa
                self.secondWalk(c, n, x + xx, y + yy, l * np.c, p)
