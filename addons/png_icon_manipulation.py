from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


def colorizeImage(pixmap:QPixmap, color:QColor):
    ''' colorizes a QPixmap with the specified color. '''
    colored_pixmap = QPixmap(pixmap.size())
    colored_pixmap.fill(Qt.transparent)

    painter = QPainter(colored_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(colored_pixmap.rect(), color)
    painter.end()

    return colored_pixmap


def resizeImage(pixmap:QPixmap, size:QSize) -> QPixmap:
    """Resizes a QPixmap to the specified width and height."""
    pixmap = pixmap.scaled(size.width(), size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return pixmap