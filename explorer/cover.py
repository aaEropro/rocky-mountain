from PySide6.QtCore import *
from PySide6.QtGui import *
import PySide6.QtGui
from PySide6.QtWidgets import *
import sys


class Cover(QFrame):
    image_path = None
    title_text = None

    title_font = QFont('Arial', 9)

    x_constraint = None
    y_constraint = None

    clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.default_bg_color = self.palette().color(self.backgroundRole()).name()

        self.setLayout(QVBoxLayout())    # set the layout
        self.setStyleSheet("QFrame")

        self.image_label = QLabel(self)    # crate the label containing the image
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.image_label)

        self.title_label = QLabel(self)
        self.title_label.setFont(self.title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.layout().addWidget(self.title_label)


    def setImage(self, image_path:str) -> None:
        ''' set the image of the cover '''
        self.image_path = image_path
        self.pixmap = QPixmap(self.image_path)    # set the image inside the pixmap
        self.image_label.setPixmap(self.pixmap)    # set the pixmap


    def setTitle(self, text:str) -> None:
        ''' set the text of the cover '''
        self.title_text = text
        self.title_label.setText(self.title_text)    # set the title in the label


    def setTitleFont(self, title_font:QFont) -> None:
        ''' sets the title of the cover '''
        self.title_font = title_font
        self.title_label.setFont(self.title_font)


    def setSizeConstraints(self, x:int, y:int) -> None:
        ''' set the maximum size of the image. it resizes the original image, while retain the original ratio. '''
        self.x_constraint = x
        self.y_constraint = y
        self.pixmap = QPixmap(self.image_path)
        self.pixmap = self.pixmap.scaled(self.x_constraint, self.y_constraint, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(self.pixmap)    # set the pixmap


    def mousePressEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.setStyleSheet("background-color: #adaca9;")
        return True
    

    def mouseReleaseEvent(self, event:QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.setStyleSheet(f"background-color: {self.default_bg_color};")
            self.clicked.emit()
        return True



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()

    widget = QWidget(window)
    widget.setLayout(QVBoxLayout())

    instance = Cover(widget)
    instance.setFrameShape(QFrame.Box)
    instance.setLineWidth(2)
    instance.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    instance.setImage('technician.jpg')
    instance.setTitle('The Technician')
    instance.setSizeConstraints(250, 600)
    widget.layout().addWidget(instance)
    window.setCentralWidget(widget)

    window.show()
    sys.exit(app.exec())