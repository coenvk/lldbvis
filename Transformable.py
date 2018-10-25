class Transformable:
    def __init__(self):
        pass

    def translate2(self, dx, dy):
        raise NotImplementedError

    def translate3(self, dx, dy, dz):
        raise NotImplementedError

    def rotate3(self, angleX, angleY, angleZ):
        raise NotImplementedError

    def scale(self, factor):
        raise NotImplementedError

