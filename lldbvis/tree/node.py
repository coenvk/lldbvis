from node_data import *
from node_geom import NodeGeometry

global_id = 0


class Node:
    def __init__(self, data=None):
        global global_id
        self.data = data
        self._parent = None
        self.children = []
        self.id = global_id
        self.depth = 0
        self.geom = NodeGeometry(self)
        global_id += 1

    def isProcessNode(self):
        return isinstance(self.data, ProcessData)

    def isThreadNode(self):
        return isinstance(self.data, ThreadData)

    def isFrameNode(self):
        return isinstance(self.data, FrameData)

    def isValueNode(self):
        return isinstance(self.data, ValueData)

    @property
    def name(self):
        return str(self.data.name)

    @property
    def x(self):
        return self.geom.x

    @property
    def y(self):
        return self.geom.y

    @property
    def z(self):
        return self.geom.z

    @property
    def absoluteX(self):
        return self.geom.absoluteX

    @property
    def absoluteY(self):
        return self.geom.absoluteY

    @property
    def absoluteZ(self):
        return self.geom.absoluteZ

    @property
    def absolutePosition(self):
        return self.geom.absolutePosition

    def __iadd__(self, other):
        if isinstance(other, Node):
            self.children.append(other)

    def __len__(self):
        return self.size()

    def size(self):
        return len(self.children)

    def totalSize(self):
        n = self.size()
        for i in range(self.size()):
            child = self[i]
            n += child.totalSize()
        return n

    def clear(self):
        self.children = []

    def validateChild(self, child):
        if child.data is None:
            return True
        if self.isProcessNode():
            return child.isThreadNode()

        if self.isThreadNode():
            return child.isFrameNode()

        if self.isFrameNode() or self.isValueNode():
            return child.isValueNode()

    def add(self, child):
        if isinstance(child, Node):
            if self.validateChild(child):
                self.children.append(child)
                child._parent = self
                child.depth = self.depth + 1
                child.updateChildDepth()
            else:
                raise TypeError('Error in implementation: should never occur')

    def addAll(self, children):
        for child in children:
            self.add(child)

    def updateChildDepth(self):
        for i in range(self.size()):
            child = self.children[i]
            child.depth = self.depth + 1
            child.updateChildDepth()

    def __int__(self):
        return self.id

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.getByIndex(item)
        elif isinstance(item, str):
            return self.getByName(item)
        return None

    def getByIndex(self, i):
        return self.children[i]

    def getById(self, id):
        if self.id == id:
            return self
        else:
            if self.size() == 0:
                return None
            for i in range(len(self.children)):
                n = self.children[i].getById(id)
                if n is not None:
                    return n
        return None

    def getByName(self, name):
        if self.name == name:
            return self
        else:
            if self.size() == 0:
                return None
            for i in range(len(self.children)):
                if self.children[i].getByName(name) is not None:
                    return self.children[i]

    def remove(self, i):
        if 0 <= i < len(self.children):
            return self.children.pop(i)

    def isRoot(self):
        return self._parent is None

    def hasChildren(self):
        return len(self.children) > 0

    def asArray(self):
        nodes = [self]
        for i in range(len(self.children)):
            nodes.extend(self.children[i].asArray())

    @property
    def parent(self):
        return self._parent

    def draw(self, widget):
        self.geom.draw(widget)

    def __str__(self):
        s = '{' + str(self.id) + ': '
        for i in range(self.size()):
            s += str(self[i]) + ' '
        s += '}'
        return s
