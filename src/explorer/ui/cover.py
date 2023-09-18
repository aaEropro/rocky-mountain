from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *



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



class Cover(QFrame):
    left_click = Signal()
    right_click = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.image_path = None
        self.title_text = None
        self.title_font = QFont('Arial', 9)
        self.x_constraint = None
        self.y_constraint = None

        self.left_mouse_clicked = False
        self.left_has_exit = False
        self.right_mouse_clicked = False
        self.right_has_exit = False

        self.default_stylesheet =   '''
                                        QFrame {
                                            background-color: rgb(27, 27, 27);
                                            border: 1px solid rgb(27, 27, 27);
                                        }
                                        QLabel {
                                            background-color: rgb(27, 27, 27);
                                            color: rgb(190, 189, 189);
                                            border: none;
                                        }
                                    '''
        
        self.clicked_stylesheet =   '''
                                        QFrame {
                                            border: 1px solid rgb(27, 27, 27);
                                            background-color: rgb(59, 58, 58);
                                        }
                                        QLabel {
                                            color: rgb(190, 189, 189);
                                            border: none;
                                        }
                                    '''


        self.setMouseTracking(True)
        self.setLayout(QVBoxLayout())    # set the layout
        self.setStyleSheet(self.default_stylesheet)

        self.image_label = QLabel(self)    # crate the label containing the image
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(self.image_label)

        self.title_widget = QWidget(self)
        self.title_layout = QHBoxLayout(self.title_widget)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.setSpacing(3)
        self.layout().addWidget(self.title_widget)

        self.title_label = QLabel(self.title_widget)
        self.title_label.setFont(self.title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_layout.addWidget(self.title_label)

        # self.three_dots = ClickableLabel(self.title_widget)
        # self.three_dots.setPixmap(QPixmap(r'assets\icons\three-dots-2.png'))
        # self.three_dots.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # self.title_layout.addWidget(self.three_dots)


    def setImage(self, image_path:str) -> None:
        ''' set the image of the cover '''
        self.image_path = image_path
        self.pixmap = QPixmap(self.image_path)    # set the image inside the pixmap
        if self.x_constraint is None:
            self.x_constraint = self.pixmap.width()
        if self.y_constraint is None:
            self.y_constraint = self.pixmap.height()
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
        x = int(x); y = int(y)
        if x == self.x_constraint and y == self.y_constraint:
            return
        self.x_constraint = x
        self.y_constraint = y
        self.pixmap = QPixmap(self.image_path)
        self.pixmap = self.pixmap.scaled(self.x_constraint, self.y_constraint, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(self.pixmap)    # set the pixmap


    def setHeightConstraint(self, height:int) -> None:
        ''' set the maximum height of the image. it resizes the image, while retain the original ratio. '''
        height = int(height)
        if height == self.y_constraint:
            return
        self.y_constraint = height
        self.pixmap = QPixmap(self.image_path)
        self.pixmap = self.pixmap.scaled(self.pixmap.width(), self.y_constraint, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(self.pixmap)    # set the pixmap


################################## CLICK HANDALING ################################################
    def mousePressEvent(self, event:QMouseEvent) -> None:
        ''' manages mouse press. '''
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.clicked_stylesheet)
            self.left_mouse_clicked = True
            self.left_has_exit = False

        elif event.button() == Qt.MouseButton.RightButton:
            self.right_mouse_clicked = True
            self.right_has_exit = False

        return True
    

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        ''' handle the mouse exiting the QFrame. '''
        main_geometry = self.rect()
        # three_dots_geometry = self.three_dots.rect()
        event_in_main_geometry = main_geometry.contains(event.pos())

        if self.left_mouse_clicked and (not event_in_main_geometry) and (not self.left_has_exit):
            self.setStyleSheet(self.default_stylesheet)
            self.left_has_exit = True
        
        elif self.left_mouse_clicked and event_in_main_geometry and self.left_has_exit:
            self.setStyleSheet(self.clicked_stylesheet)
            self.left_has_exit = False

        elif self.right_mouse_clicked and (not event_in_main_geometry) and (not self.right_has_exit):
            self.right_has_exit = True
        
        elif self.right_mouse_clicked and event_in_main_geometry and self.right_has_exit:
            self.right_has_exit = False

        return super().mouseMoveEvent(event)
    

    def mouseReleaseEvent(self, event:QMouseEvent) -> None:
        ''' manages mouse release. '''
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.default_stylesheet)
            self.left_mouse_clicked = False
            if not self.left_has_exit:
                self.left_click.emit()
            self.left_has_exit = False

        elif event.button() == Qt.MouseButton.RightButton:
            self.right_mouse_clicked = False
            if not self.right_has_exit:
                self.right_click.emit()
            self.right_has_exit = False

        return True