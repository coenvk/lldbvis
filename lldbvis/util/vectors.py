from math import *
from transform import Transformable


class Vector2(Transformable):
    def __init__(self, x=0.0, y=0.0):
        Transformable.__init__(self)
        self.x = x
        self.y = y

    def __copy__(self):
        return Vector2(self.x, self.y)

    def translate2(self, dx, dy):
        self.x += dx
        self.y += dy

    def translate3(self, dx, dy, dz):
        self.x += dx
        self.y += dy

    def rotate3(self, angleX, angleY, angleZ):
        v = Vector3(self.x, self.y, 0)
        x = v.x
        y = v.y
        v.x = x * cos(angleZ) - y * sin(angleZ)
        v.y = x * sin(angleZ) + y * cos(angleZ)
        y = v.y
        z = v.z
        v.y = y * cos(angleX) - z * sin(angleX)
        v.z = y * sin(angleX) + z * cos(angleX)
        z = v.z
        x = v.x
        v.z = z * cos(angleY) - x * sin(angleY)
        v.x = z * sin(angleY) + x * cos(angleY)
        self.x = v.x
        self.y = v.y

    def scale(self, factor):
        self.x *= factor
        self.y *= factor

    @staticmethod
    def zero():
        return Vector2()

    @staticmethod
    def unitY():
        return Vector2(0, 1)

    @staticmethod
    def unitX():
        return Vector2(1, 0)

    def __div__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x / other.x, self.y / other.y)
        elif isinstance(other, (int, float)):
            return Vector2(self.x / other, self.y / other)

    def __rdiv__(self, other):
        if isinstance(other, Vector2):
            return Vector2(other.x / self.x, other.y / self.y)
        elif isinstance(other, (int, float)):
            return Vector2(other / self.x, other / self.y)

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        elif isinstance(other, (int, float)):
            return Vector2(self.x + other, self.y + other)

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        elif isinstance(other, (int, float)):
            return Vector2(self.x - other, self.y - other)

    def __rsub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(other.x - self.x, other.y - self.y)
        elif isinstance(other, (int, float)):
            return Vector2(other - self.x, other - self.y)

    def __mul__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        elif isinstance(other, (int, float)):
            return Vector2(self.x * other, self.y * other)

    def __pow__(self, power):
        return Vector2(self.x ** power, self.y ** power)

    def __iadd__(self, other):
        if isinstance(other, Vector2):
            self.x += other.x
            self.y += other.y
        elif isinstance(other, (int, float)):
            self.x += other
            self.y += other
        return self

    def __idiv__(self, other):
        if isinstance(other, Vector2):
            self.x /= other.x
            self.y /= other.y
        elif isinstance(other, (int, float)):
            self.x /= other
            self.y /= other
        return self

    def __isub__(self, other):
        if isinstance(other, Vector2):
            self.x -= other.x
            self.y -= other.y
        elif isinstance(other, (int, float)):
            self.x -= other
            self.y -= other
        return self

    def __imul__(self, other):
        if isinstance(other, Vector2):
            self.x *= other.x
            self.y *= other.y
        elif isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
        return self

    def __ipow__(self, other):
        self.x **= other
        self.y **= other
        return self

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __len__(self):
        return int(self.length())

    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def distance(self, v):
        return (self - v).length()

    def dot(self, v):
        return self.x * v.x + self.y * v.y

    def det(self, v):
        return self.x * v.y - self.y * v.x

    def unit(self):
        if self.length() > 0:
            return self / self.length()
        return self

    def asArray(self):
        return [self.x, self.y]

    def angle(self, v=None):
        if v is None:
            v = self.unitX()
        return acos(self.dot(v) / (self.length() * v.length()))

    def setTo(self, v):
        self.x = v.x
        self.y = v.y

    def rounded(self, threshold=None):
        if threshold is None:
            return Vector2(round(self.x), round(self.y))
        x = self.x if abs(self.x - round(self.x)) > threshold else round(self.x)
        y = self.y if abs(self.y - round(self.y)) > threshold else round(self.y)
        return Vector2(x, y)

    def __str__(self):
        return '{' + str(self.x) + ',' + str(self.y) + '}'


class Vector3(Transformable):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        Transformable.__init__(self)
        self.x = x
        self.y = y
        self.z = z

    def __copy__(self):
        return Vector3(self.x, self.y, self.z)

    def translate2(self, dx, dy):
        self.x += dx
        self.y += dy

    def translate3(self, dx, dy, dz):
        self.x += dx
        self.y += dy
        self.z += dz

    def rotate3(self, angleX, angleY, angleZ):
        v = Vector3(self.x, self.y, self.z)
        x = v.x
        y = v.y
        v.x = x * cos(angleZ) - y * sin(angleZ)
        v.y = x * sin(angleZ) + y * cos(angleZ)
        y = v.y
        z = v.z
        v.y = y * cos(angleX) - z * sin(angleX)
        v.z = y * sin(angleX) + z * cos(angleX)
        z = v.z
        x = v.x
        v.z = z * cos(angleY) - x * sin(angleY)
        v.x = z * sin(angleY) + x * cos(angleY)
        self.setTo(v)

    def scale(self, factor):
        self.x *= factor
        self.y *= factor
        self.z *= factor

    @staticmethod
    def zero():
        return Vector3()

    @staticmethod
    def unitY():
        return Vector3(0, 1, 0)

    @staticmethod
    def unitX():
        return Vector3(1, 0, 0)

    @staticmethod
    def unitZ():
        return Vector3(0, 0, 1)

    def __div__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x / other.x, self.y / other.y, self.z / other.z)
        elif isinstance(other, (int, float)):
            return Vector3(self.x / other, self.y / other, self.z / other)

    def __rdiv__(self, other):
        if isinstance(other, Vector3):
            return Vector3(other.x / self.x, other.y / self.y, other.z / self.z)
        elif isinstance(other, (int, float)):
            return Vector3(other / self.x, other / self.y, other / self.z)

    def __add__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, (int, float)):
            return Vector3(self.x + other, self.y + other, self.z + other)

    def __sub__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, (int, float)):
            return Vector3(self.x - other, self.y - other, self.z - other)

    def __rsub__(self, other):
        if isinstance(other, Vector3):
            return Vector3(other.x - self.x, other.y - self.y, other.z - self.z)
        elif isinstance(other, (int, float)):
            return Vector3(other - self.x, other - self.y, other - self.z)

    def __mul__(self, other):
        if isinstance(other, Vector3):
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        elif isinstance(other, (int, float)):
            return Vector3(self.x * other, self.y * other, self.z * other)

    def __pow__(self, power):
        return Vector3(self.x ** power, self.y ** power, self.z ** power)

    def __iadd__(self, other):
        if isinstance(other, Vector3):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        elif isinstance(other, (int, float)):
            self.x += other
            self.y += other
            self.z += other
        return self

    def __idiv__(self, other):
        if isinstance(other, Vector3):
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z
        elif isinstance(other, (int, float)):
            self.x /= other
            self.y /= other
            self.z /= other
        return self

    def __isub__(self, other):
        if isinstance(other, Vector3):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
        elif isinstance(other, (int, float)):
            self.x -= other
            self.y -= other
            self.z -= other
        return self

    def __imul__(self, other):
        if isinstance(other, Vector3):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        elif isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
            self.z *= other
        return self

    def __ipow__(self, other):
        self.x **= other
        self.y **= other
        self.z **= other
        return self

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y or self.z != other.z

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    def __len__(self):
        return int(self.length())

    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def distance(self, v):
        return (self - v).length()

    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z

    def cross(self, v):
        return Vector3(self.y * v.z - self.z * v.y, self.z * v.x - self.x * v.z, self.x * v.y - self.y * v.x)

    def unit(self):
        if self.length() > 0:
            return self / self.length()
        return self

    def asArray(self):
        return [self.x, self.y, self.z]

    def asVector2(self):
        return Vector2(self.x, self.y)

    def angle(self, v=None):
        if v is None:
            v = self.unitX()
        if v.length() == 0 or self.length() == 0:
            return 0

        return atan2(self.cross(v).length(), self.dot(v))

    def setTo(self, v):
        self.x = v.x
        self.y = v.y
        self.z = v.z

    def rounded(self, threshold=None):
        if threshold is None:
            return Vector3(round(self.x), round(self.y), round(self.z))
        x = self.x if abs(self.x - round(self.x)) > threshold else round(self.x)
        y = self.y if abs(self.y - round(self.y)) > threshold else round(self.y)
        z = self.z if abs(self.z - round(self.z)) > threshold else round(self.z)
        return Vector3(x, y, z)

    def __str__(self):
        return '{' + str(self.x) + ',' + str(self.y) + ',' + str(self.z) + '}'


class Vector4(Transformable):
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        Transformable.__init__(self)
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __copy__(self):
        return Vector4(self.x, self.y, self.z, self.w)

    def translate2(self, dx, dy):
        self.x += dx
        self.y += dy

    def translate3(self, dx, dy, dz):
        self.x += dx
        self.y += dy
        self.z += dz

    def rotate3(self, angleX, angleY, angleZ):
        v = Vector3(self.x, self.y, self.z)
        x = v.x
        y = v.y
        v.x = x * cos(angleZ) - y * sin(angleZ)
        v.y = x * sin(angleZ) + y * cos(angleZ)
        y = v.y
        z = v.z
        v.y = y * cos(angleX) - z * sin(angleX)
        v.z = y * sin(angleX) + z * cos(angleX)
        z = v.z
        x = v.x
        v.z = z * cos(angleY) - x * sin(angleY)
        v.x = z * sin(angleY) + x * cos(angleY)
        self.x = v.x
        self.y = v.y
        self.z = v.z

    def scale(self, factor):
        self.x *= factor
        self.y *= factor
        self.z *= factor

    @staticmethod
    def zero():
        return Vector4()

    @staticmethod
    def unitY():
        return Vector4(0, 1, 0, 0)

    @staticmethod
    def unitX():
        return Vector4(1, 0, 0, 0)

    @staticmethod
    def unitZ():
        return Vector4(0, 0, 1, 0)

    @staticmethod
    def unitW():
        return Vector4(0, 0, 0, 1)

    def __div__(self, other):
        if isinstance(other, Vector4):
            return Vector4(self.x / other.x, self.y / other.y, self.z / other.z, self.w / other.w)
        elif isinstance(other, (int, float)):
            return Vector4(self.x / other, self.y / other, self.z / other, self.w / other)

    def __rdiv__(self, other):
        if isinstance(other, Vector4):
            return Vector4(other.x / self.x, other.y / self.y, other.z / self.z, other.w / self.w)
        elif isinstance(other, (int, float)):
            return Vector4(other / self.x, other / self.y, other / self.z, other / self.w)

    def __add__(self, other):
        if isinstance(other, Vector4):
            return Vector4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
        elif isinstance(other, (int, float)):
            return Vector4(self.x + other, self.y + other, self.z + other, self.w + other)

    def __sub__(self, other):
        if isinstance(other, Vector4):
            return Vector4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)
        elif isinstance(other, (int, float)):
            return Vector4(self.x - other, self.y - other, self.z - other, self.w - other)

    def __rsub__(self, other):
        if isinstance(other, Vector4):
            return Vector4(other.x - self.x, other.y - self.y, other.z - self.z, other.w - self.w)
        elif isinstance(other, (int, float)):
            return Vector4(other - self.x, other - self.y, other - self.z, other - self.w)

    def __mul__(self, other):
        if isinstance(other, Vector4):
            return Vector4(self.x * other.x, self.y * other.y, self.z * other.z, self.w * other.w)
        elif isinstance(other, (int, float)):
            return Vector4(self.x * other, self.y * other, self.z * other, self.w * other)

    def __pow__(self, power):
        return Vector4(self.x ** power, self.y ** power, self.z ** power, self.w ** power)

    def __iadd__(self, other):
        if isinstance(other, Vector4):
            self.x += other.x
            self.y += other.y
            self.z += other.z
            self.w += other.w
        elif isinstance(other, (int, float)):
            self.x += other
            self.y += other
            self.z += other
            self.w += other
        return self

    def __idiv__(self, other):
        if isinstance(other, Vector4):
            self.x /= other.x
            self.y /= other.y
            self.z /= other.z
            self.w /= other.w
        elif isinstance(other, (int, float)):
            self.x /= other
            self.y /= other
            self.z /= other
            self.w /= other
        return self

    def __isub__(self, other):
        if isinstance(other, Vector4):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
            self.w -= other.w
        elif isinstance(other, (int, float)):
            self.x -= other
            self.y -= other
            self.z -= other
            self.w -= other
        return self

    def __imul__(self, other):
        if isinstance(other, Vector4):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
            self.w *= other.w
        elif isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
            self.z *= other
            self.w *= other
        return self

    def __ipow__(self, other):
        self.x **= other
        self.y **= other
        self.z **= other
        self.w **= other
        return self

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z and self.w == other.w

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y or self.z != other.z or self.w != other.w

    def __neg__(self):
        return Vector4(-self.x, -self.y, -self.z, -self.w)

    def __len__(self):
        return int(self.length())

    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)

    def distance(self, v):
        return (self - v).length()

    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z + self.w * v.w

    def unit(self):
        if self.length() > 0:
            return self / self.length()
        return self

    def asArray(self):
        return [self.x, self.y, self.z, self.w]

    def asVector3(self):
        return Vector3(self.x, self.y, self.z)

    def setTo(self, v):
        self.x = v.x
        self.y = v.y
        self.z = v.z
        self.w = v.w

    def rounded(self, threshold=None):
        if threshold is None:
            return Vector4(round(self.x), round(self.y), round(self.z), round(self.w))
        x = self.x if abs(self.x - round(self.x)) > threshold else round(self.x)
        y = self.y if abs(self.y - round(self.y)) > threshold else round(self.y)
        z = self.z if abs(self.z - round(self.z)) > threshold else round(self.z)
        w = self.w if abs(self.w - round(self.w)) > threshold else round(self.w)
        return Vector4(x, y, z, w)

    def __str__(self):
        return '{' + str(self.x) + ',' + str(self.y) + ',' + str(self.z) + ',' + str(self.w) + '}'
