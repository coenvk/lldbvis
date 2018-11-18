from lldbvis.util.vectors import Vector4


class Light:
    def __init__(self, position=Vector4(), ambient=Vector4(), diffuse=Vector4(), specular=Vector4()):
        self.position = position
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular

