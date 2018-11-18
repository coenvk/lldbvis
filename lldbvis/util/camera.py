from math import *

from lldbvis.settings import constants
from lldbvis.util.transform import Transformable


class Camera(Transformable):
    def __init__(self, movement_speed=constants.DEFAULT_CAMERA_MOVEMENT_SPEED,
                 position=constants.DEFAULT_CAMERA_POSITION, euler_angles=constants.DEFAULT_CAMERA_EULER_ANGLES):
        Transformable.__init__(self)
        self.position = position
        self.eulerAngles = euler_angles
        self.movementSpeed = movement_speed

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
