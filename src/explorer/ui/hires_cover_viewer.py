from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import os

from addons.overlay import OverlayWidget
from addons.png_icon_manipulation import colorizeImage



class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.clicked.emit()
        return True
    
    def setHover(self):
        self.setStyleSheet('''
            QLabel:hover
            {
                background-color: rgb(70, 69, 69);
            }''')



class ImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = self._scene.addPixmap(QPixmap())
        self.setScene(self._scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
            self.fitInView(self._photo.pixmap().rect(), Qt.KeepAspectRatio)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.updateViewer()

    def zoomFactor(self):
        return self._zoom

    def wheelEvent(self, event):
        if not self._photo.pixmap().isNull():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView(self._photo.pixmap().rect(), Qt.KeepAspectRatio)
            else:
                self._zoom = 0

    def updateViewer(self):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self._photo.isVisible():
                self.fitInView(self._photo.pixmap().rect(), Qt.KeepAspectRatio)
            self.updateScene([self.sceneRect()])

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        return super().resizeEvent(event)



class HighResViewer(OverlayWidget):
    save = Signal(object, dict)
    cancel = Signal()

    def __init__(self, parent, path_to_image):
        super().__init__(parent)
        
        self.path_to_image = path_to_image
        self.master_layout = QVBoxLayout(self)
        self.master_layout.setContentsMargins(3, 3, 3, 3)
        self.master_layout.setSpacing(0)

        # self.container_widget = QWidget(self)
        # self.container_widget.setStyleSheet("""
        #                                     QWidget {
        #                                         border: 2px solid rgb(42, 41, 41);
        #                                     }
        #                                     QPushButton {
        #                                         border: none;
        #                                         background-color: none;
        #                                     }
        #                                     QFrame {
        #                                         border: none;
        #                                         background-color: none;
        #                                     }
        #                                 """)
        # self.container_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.master_layout.addWidget(self.container_widget, alignment=Qt.AlignCenter)
        # self.container_layout = QVBoxLayout(self.container_widget)
        # self.container_widget.setLayout(self.container_layout)

        # self.image_pixmap = QPixmap(self.path_to_image)
        # self.image_pixmap = self.image_pixmap.scaled(QSize(550, 550), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # if self.image_pixmap.isNull():
        #     print("Failed to load image!")
        #     return

        # self.image_label = QLabel(self.container_widget)
        # self.image_label.setPixmap(self.image_pixmap)
        # self.container_layout.addWidget(self.image_label)  # Add image_label to container_layout.

        pixmap = QPixmap(self.path_to_image)

        self.image_viewer = ImageViewer()
        self.image_viewer.setStyleSheet('border: none;')
        self.master_layout.addWidget(self.image_viewer)
        self.image_viewer.setPhoto(pixmap)

        close_icon = QPixmap(os.path.join('assets', 'icons', 'close-in-circle.png'))
        close_icon = colorizeImage(close_icon, QColor(206, 206, 206))
        self.close_btn = ClickableLabel(self)
        self.close_btn.setFixedSize(close_icon.size())
        # self.close_btn.setStyleSheet('background:green;')
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setPixmap(close_icon)
        self.close_btn.move(QPoint(self.width()-self.close_btn.sizeHint().width()-3, 3))


    def resizeEvent(self, event: QResizeEvent) -> None:
        self.close_btn.move(QPoint(self.width()-self.close_btn.sizeHint().width()-3, 3))
        return super().resizeEvent(event)