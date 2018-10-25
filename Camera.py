from Vector import Vector3, Vector2
from Transformable import Transformable
from math import pi


class Camera(Transformable):
    def __init__(self, movementSpeed=0.15, position=Vector3(0, 0, 10), eulerAngles=Vector3()):
        Transformable.__init__(self)
        self.position = position
        self.eulerAngles = eulerAngles
        self.movementSpeed = movementSpeed

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
    def eulerAngleXDeg(self):
        return self.eulerAngles.x * 180 / pi

    @property
    def eulerAngleYDeg(self):
        return self.eulerAngles.y * 180 / pi

    @property
    def eulerAngleZDeg(self):
        return self.eulerAngles.z * 180 / pi

    @property
    def eulerAngleXRad(self):
        return self.eulerAngles.x

    @property
    def eulerAngleYRad(self):
        return self.eulerAngles.y

    @property
    def eulerAngleZRad(self):
        return self.eulerAngles.z

    def translate2(self, dx, dy):
        self.position.translate2(dx, dy)

    def translate3(self, dx, dy, dz):
        self.position.translate3(dx, dy, dz)

    def rotate3(self, angleX, angleY, angleZ):
        self.eulerAngles.translate3(angleX, angleY, angleZ)

    def scale(self, factor):
        self.position.scale(factor)
        self.eulerAngles.scale(factor)

    def distance(self, v):
        rel_v = v.__copy__()
        rel_v.rotate3(self.eulerAngleXRad, self.eulerAngleYRad, self.eulerAngleZRad)
        dir = self.position - rel_v
        return dir.length()
