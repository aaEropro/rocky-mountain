from PySide6.QtCore import *
import PySide6.QtCore
from PySide6.QtGui import *
import PySide6.QtGui
from PySide6.QtWidgets import *
import sys
from addons.png_icon_manipulation import colorizeImage, resizeImage
import os


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


class TitleBar(QWidget):

    def __init__(self):
        super().__init__()

        self.h_size = 36
        self.window_instance:QMainWindow = None
        self.start_move_pos:QPoint = QPoint()
        stylesheet = '''
            QWidget, QLabel
            {
                background-color: rgb(33, 32, 32);
            }
        '''


        self.hbox_layout = QHBoxLayout(self)
        self.hbox_layout.setSpacing(0)
        self.hbox_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.hbox_layout)
        self.setStyleSheet(stylesheet)


        self.logo_widget = QWidget(self)
        self.logo_widget.setLayout(QHBoxLayout(self.logo_widget))
        self.logo_widget.layout().setContentsMargins(4, 0, 4, 0)
        self.logo_widget.layout().setSpacing(0)
        self.hbox_layout.addWidget(self.logo_widget)
        self.logo_label = QLabel(self.logo_widget)    # left corner logo
        self.logo_pixmap = QPixmap(os.path.join('logos', 'rm_logo.png'))
        self.logo_pixmap = self.logo_pixmap.scaled(self.h_size, self.h_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_widget.layout().addWidget(self.logo_label)


        self.menus_widget = QWidget(self)
        self.menu_layout = QHBoxLayout(self.menus_widget)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(0)
        self.menus_widget.setLayout(self.menu_layout)
        self.hbox_layout.addWidget(self.menus_widget)


        self.title_label = QLabel(self)
        self.title_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.title_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.hbox_layout.addWidget(self.title_label)


        self.window_buttons_widget = QWidget(self)
        self.window_buttons_layout = QHBoxLayout(self.window_buttons_widget)
        self.window_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.window_buttons_layout.setSpacing(0)
        self.window_buttons_widget.setLayout(self.window_buttons_layout)
        self.hbox_layout.addWidget(self.window_buttons_widget)


        # self.logo_widget.setStyleSheet('background:red')
        # self.logo_label.setStyleSheet('background:purple')
        # self.menus_widget.setStyleSheet('background:green')
        # self.title_label.setStyleSheet('background:blue')
        # self.window_buttons_widget.setStyleSheet('background:magenta')


        self.createWindowManipulation()
        self.createButtons()


    def setWindowInstance(self, instance:QMainWindow) -> None:
        ''' sets the main window instance. '''
        self.window_instance = instance


    def setTitle(self, title:str) -> None:
        self.title_label.clear()
        self.title_label.setText(title)

    
    def setTitleFont(self, font:QFont) -> None:
        ''' set the font of the title. '''
        self.title_label.setFont(font)


    def createWindowManipulation(self, icon_size:int=28, color:QColor=QColor(206, 206, 206)) -> None:
        ''' creates the minimize, maximize and close window buttons. '''
        icon_size = QSize(icon_size, icon_size)

        min_icon = colorizeImage(QPixmap(os.path.join('icons', 'minimize.png')), color)
        min_icon = resizeImage(min_icon, icon_size)
        max_icon = colorizeImage(QPixmap(os.path.join('icons', 'maximize.png')), color)
        max_icon = resizeImage(max_icon, icon_size)
        close_icon = colorizeImage(QPixmap(os.path.join('icons', 'close.png')), color)
        close_icon = resizeImage(close_icon, icon_size)

        self.minimize_button = ClickableLabel(self.window_buttons_widget)
        self.minimize_button.setFixedSize(self.h_size, self.h_size)
        self.minimize_button.setStyleSheet("background-color: green;")
        self.minimize_button.setAlignment(Qt.AlignCenter|Qt.AlignCenter)
        self.minimize_button.setPixmap(min_icon)
        self.minimize_button.setHover()
        self.minimize_button.clicked.connect(self.toggleMinimized)
        self.window_buttons_layout.addWidget(self.minimize_button)


        self.maximize_button = ClickableLabel(self.window_buttons_widget)
        self.maximize_button.setFixedSize(self.h_size, self.h_size)
        self.maximize_button.setStyleSheet("background-color: blue;")
        self.maximize_button.setAlignment(Qt.AlignCenter|Qt.AlignCenter)
        self.maximize_button.setPixmap(max_icon)
        self.maximize_button.setHover()
        self.maximize_button.clicked.connect(self.toggleMaximized)
        self.window_buttons_layout.addWidget(self.maximize_button)


        self.close_button = ClickableLabel(self.window_buttons_widget)
        self.close_button.setFixedSize(self.h_size, self.h_size)
        self.close_button.setStyleSheet("background-color: green;")
        self.close_button.setAlignment(Qt.AlignCenter|Qt.AlignCenter)
        self.close_button.setPixmap(close_icon)
        self.close_button.clicked.connect(self.closeWindow)
        self.close_button.setStyleSheet("QLabel:hover{background-color: red;}")
        self.window_buttons_layout.addWidget(self.close_button)


    def toggleMinimized(self):
        if self.window_instance is None:
            return
        
        if self.window_instance.isMinimized():
            self.window_instance.showNormal()
        else:
            self.window_instance.showMinimized()


    def toggleMaximized(self):
        if self.window_instance is None:
            return
        
        if self.window_instance.isMaximized():
            self.window_instance.showNormal()
        else:
            self.window_instance.showMaximized()


    def closeWindow(self):
        if self.window_instance is None:
            return
        
        self.window_instance.close()


    def mousePressEvent(self, event):
        # Check if the event occurred within the title_label's geometry
        if event.button() == Qt.LeftButton and self.title_label.geometry().contains(event.position().toPoint()):  # Updated this line
            self.start_move_pos = event.globalPosition().toPoint()
            event.accept()


    def mouseMoveEvent(self, event):
        if (event.buttons() == Qt.LeftButton) and (self.title_label.geometry().contains(event.position().toPoint())):  # Updated this line
            if self.window_instance.isMaximized():
                self.window_instance.showNormal()
                middle_width = self.window_instance.width()//2
                diff = event.globalPosition().toPoint() - QPoint(middle_width, self.height()//2)
                self.window().move(self.window().pos() + diff)
                self.start_move_pos = event.globalPosition().toPoint()
                event.accept()
            else:
                diff = event.globalPosition().toPoint() - self.start_move_pos
                self.window().move(self.window().pos() + diff)
                self.start_move_pos = event.globalPosition().toPoint()
                event.accept()


    def createButtons(self, icon_size:int=20):
        size = self.h_size-self.menu_layout.contentsMargins().top()-self.menu_layout.contentsMargins().bottom()
        if size < icon_size:
            icon_size = size
        icon_size = QSize(icon_size, icon_size)

        settings_icon = colorizeImage(QPixmap(os.path.join('icons', 'icons8-settings-96.png')), QColor(206, 206, 206))
        settings_icon = resizeImage(settings_icon, icon_size)

        self.settings_button = ClickableLabel()
        self.settings_button.setFixedSize(size, size)
        self.settings_button.setPixmap(settings_icon)
        self.settings_button.setHover()
        self.settings_button.setAlignment(Qt.AlignLeft|Qt.AlignCenter)
        self.menu_layout.addWidget(self.settings_button)


