import sys

from PyQt4.QtCore import Qt

from lldbvis.settings import constants
from lldbvis.util.vectors import Vector3, Vector2


class Keyboard:
    def __init__(self):
        pass

    def key_press(self, event):
        pass

    def key_release(self, event):
        pass


class Mouse:
    def __init__(self, mouse_sensitivity=constants.DEFAULT_MOUSE_SENSITIVITY, zoom_speed=constants.DEFAULT_ZOOM_SPEED,
                 min_zoom=constants.DEFAULT_MINIMAL_ZOOM, max_zoom=constants.DEFAULT_MAXIMAL_ZOOM):
        self.leftPressed = False
        self.rightPressed = False
        self.mouseDrag = False
        self.mousePos = Vector2()
        self.zoomSpeed = zoom_speed
        self.minZoom = min_zoom
        self.maxZoom = max_zoom
        self.mouseSensitivity = mouse_sensitivity

    def mouse_press(self, event):
        pass

    def mouse_release(self, event):
        pass

    def mouse_move(self, event):
        pass

    def mouse_wheel(self, event):
        pass

    def mouse_double_click(self, event):
        pass


class Input(Mouse, Keyboard):
    def __init__(self, camera):
        Mouse.__init__(self)
        Keyboard.__init__(self)
        self.camera = camera

    def key_press(self, event):
        if event.key() == Qt.Key_Escape:
            sys.exit(1)
        else:
            key = event.key()
            movement = Vector3()
            if key == Qt.Key_W:
                movement -= Vector3.unitZ()
            elif key == Qt.Key_S:
                movement += Vector3.unitZ()
            elif key == Qt.Key_A:
                movement -= Vector3.unitX()
            elif key == Qt.Key_D:
                movement += Vector3.unitX()
            elif key == Qt.Key_E:
                movement += Vector3.unitY()
            elif key == Qt.Key_Q:
                movement -= Vector3.unitY()
            movement *= self.camera.movementSpeed
            self.camera.position += movement

    def mouse_press(self, event):
        if event.buttons() == Qt.LeftButton:
            self.leftPressed = True
        elif event.buttons() == Qt.RightButton:
            self.rightPressed = True

    def mouse_release(self, event):
        self.mouseDrag = False
        if self.leftPressed:
            self.leftPressed = False
        elif self.rightPressed:
            self.rightPressed = False

    def mouse_move(self, event):
        buttons = event.buttons()
        x = event.x()
        y = event.y()
        if buttons == Qt.LeftButton:
            dx = x - self.mousePos.x
            dy = y - self.mousePos.y
            self.mouseDrag = Vector2(dx, dy).length() > constants.MINIMAL_MOUSE_DRAG_INTENSITY or self.mouseDrag
            dx *= self.mouseSensitivity
            dy *= self.mouseSensitivity
            self.camera.eulerAngles.x += dy
            self.camera.eulerAngles.y += dx
        else:
            self.mouseDrag = False

        self.mousePos.x = x
        self.mousePos.y = y

    def mouse_wheel(self, event):
        self.camera.position.z -= event.delta() * self.zoomSpeed
        if self.camera.position.z < self.maxZoom:
            self.camera.position.z = self.maxZoom
        elif self.camera.position.z > self.minZoom:
            self.camera.position.z = self.minZoom
