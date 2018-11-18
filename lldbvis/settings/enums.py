from lldbvis.util.enums import ColorEnum, Color3


class ColorScheme(ColorEnum):
    PROCESS_NODE = Color3(1, 0, 0)
    THREAD_NODE = Color3(0, 1, 0)
    FRAME_NODE = Color3(0, 0, 1)
    VALUE_NODE = Color3(1, 0.5, 0)

    DEFAULT = Color3(1, 1, 1)
