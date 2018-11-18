from lldbvis.events.dispatcher import Signal


PauseDebugger = Signal()
EndDebugger = Signal()
SetupDebugger = Signal()
StartDebugger = Signal()
LogDebugger = Signal()

SelectNode = Signal()
OpenDeclaration = Signal()
