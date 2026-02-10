from PySide6 import QtWidgets, QtCore, QtGui 
from typing import Optional

class ZoomableGraphicsView(QtWidgets.QGraphicsView):
    """
    Allows zoom in/out and drag functionality by using a 
    mouse wheel or trackpad - Ctrl+scroll.
    """
    def __init__(self, scene: QtWidgets.QWidget, parent: Optional[QtWidgets.QWidget] = None) -> None:
        print(parent)
        super().__init__(scene, parent)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        # current zoom level
        self._zoom: float = 1.0 
    
    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        if event.modifiers() & QtCore.Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self._zoom *= 1.15
            else:
                self._zoom /= 1.15

            # limit zooming too far out/in
            self._zoom = max(0.2, min(self._zoom, 3.0)) 
            self.setTransform(QtGui.QTransform().scale(self._zoom, self._zoom))
            event.accept()
        else:
            super().wheelEvent(event)

