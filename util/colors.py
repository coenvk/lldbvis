class Color3:
    def __init__(self, r=0.0, g=0.0, b=0.0):
        self.r = r
        self.g = g
        self.b = b

    def __copy__(self):
        color = Color3()
        color.r = self.r
        color.g = self.g
        color.b = self.b
        return color

    def inverse(self):
        return Color3(1 - self.r, 1 - self.g, 1 - self.b)

    @staticmethod
    def red():
        return Color3(1, 0, 0)

    @staticmethod
    def green():
        return Color3(0, 1, 0)

    @staticmethod
    def blue():
        return Color3(0, 0, 1)

    @staticmethod
    def yellow():
        return Color3(1, 1, 0)

    @staticmethod
    def white():
        return Color3(1, 1, 1)

    @staticmethod
    def black():
        return Color3(0, 0, 0)

    @staticmethod
    def orange():
        return Color3(1, 0.5, 0)

    @staticmethod
    def cyan():
        return Color3(0, 1, 1)

    @staticmethod
    def magenta():
        return Color3(1, 0, 1)


