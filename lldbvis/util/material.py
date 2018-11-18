from lldbvis.util.vectors import Vector4
from OpenGL.GL import *


class Material:
    def __init__(self, ambient=Vector4(), diffuse=Vector4(), specular=Vector4(), emission=Vector4(), shininess=0.0):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.emission = emission
        self.shininess = shininess * 128

    def setGL(self):
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.specular.asArray())
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, self.shininess)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.diffuse.asArray())
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.ambient.asArray())
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, self.emission.asArray())

    @staticmethod
    def silver():
        return Material(
            Vector4(0.19225, 0.19225, 0.19225, 1),
            Vector4(0.50754, 0.50754, 0.50754, 1),
            Vector4(0.508273, 0.508273, 0.508273, 1),
            shininess=0.4)

    @staticmethod
    def chrome():
        return Material(
            Vector4(0.25, 0.25, 0.25, 1),
            Vector4(0.4, 0.4, 0.4, 1),
            Vector4(0.774597, 0.774597, 0.774597, 1),
            shininess=0.6)

    @staticmethod
    def red_plastic():
        return Material(
            Vector4(0, 0, 0, 1),
            Vector4(0.5, 0, 0, 1),
            Vector4(0.7, 0.6, 0.6, 1),
            shininess=0.25)

