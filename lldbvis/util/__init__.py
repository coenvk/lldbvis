from light import Light
from material import Material
from camera import Camera
import transform
import vectors

__all__ = ['Light', 'Material', 'Camera', 'transform', 'vectors', 'resource_path']


def resource_path(file_name):
    return 'icons/' + file_name
