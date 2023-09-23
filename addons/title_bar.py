from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import os

from addons.png_icon_manipulation import colorizeImage, resizeImage

DIR = os.path.dirname(os.path.abspath(__import__('__main__').__file__))

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
    '''
        a title bar widget, with support for window dragging and closing/minimize/maximize.
    '''

    def __init__(self):
        super().__init__()

        self.h_size = 36
        self.window_instance:QMainWindow = None
        self.start_move_pos:QPoint = QPoint()
        self._window_normal_size:QRect = QRect()
        stylesheet = '''
            QWidget, QLabel
            {
                background-color: rgb(24, 24, 24);
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
        self.logo_pixmap = QPixmap(os.path.join(DIR, 'assets', 'logos', 'rm_logo.png'))
        self.logo_pixmap = self.logo_pixmap.scaled(self.h_size, self.h_size, 
                                                   Qt.AspectRatioMode.KeepAspectRatio, 
                                                   Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_widget.layout().addWidget(self.logo_label)


        self.menus_widget = QWidget(self)
        self.menu_layout = QHBoxLayout(self.menus_widget)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(0)
        self.menus_widget.setLayout(self.menu_layout)
        self.hbox_layout.addWidget(self.menus_widget)


        self.title_label = QLabel(self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter|Qt.AlignmentFlag.AlignCenter)
        self.title_label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
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
        ''' set the title on the titlebar. '''
        self.title_label.clear()
        self.title_label.setText(title)

    
    def setTitleFont(self, font:QFont) -> None:
        ''' set the font of the title. '''
        self.title_label.setFont(font)


    def createWindowManipulation(self, icon_size:int=16, color:QColor=QColor(206, 206, 206)) -> None:
        ''' creates the minimize, maximize and close window buttons. '''
        icon_size = QSize(icon_size, icon_size)

        min_icon = colorizeImage(QPixmap(os.path.join(DIR, 'assets', 'icons', 'minimize.png')), color)
        min_icon = resizeImage(min_icon, icon_size)
        max_icon = colorizeImage(QPixmap(os.path.join(DIR, 'assets', 'icons', 'maximize.png')), color)
        max_icon = resizeImage(max_icon, icon_size)
        close_icon = colorizeImage(QPixmap(os.path.join(DIR, 'assets', 'icons', 'close.png')), color)
        close_icon = resizeImage(close_icon, icon_size)

        self.minimize_button = ClickableLabel(self.window_buttons_widget)
        self.minimize_button.setFixedSize(self.h_size, self.h_size)
        self.minimize_button.setStyleSheet("background-color: green;")
        self.minimize_button.setAlignment(Qt.AlignmentFlag.AlignCenter|Qt.AlignmentFlag.AlignCenter)
        self.minimize_button.setPixmap(min_icon)
        self.minimize_button.setHover()
        self.minimize_button.clicked.connect(self.toggleMinimized)
        self.window_buttons_layout.addWidget(self.minimize_button)


        self.maximize_button = ClickableLabel(self.window_buttons_widget)
        self.maximize_button.setFixedSize(self.h_size, self.h_size)
        self.maximize_button.setStyleSheet("background-color: blue;")
        self.maximize_button.setAlignment(Qt.AlignmentFlag.AlignCenter|Qt.AlignmentFlag.AlignCenter)
        self.maximize_button.setPixmap(max_icon)
        self.maximize_button.setHover()
        self.maximize_button.clicked.connect(self.toggleMaximized)
        self.window_buttons_layout.addWidget(self.maximize_button)


        self.close_button = ClickableLabel(self.window_buttons_widget)
        self.close_button.setFixedSize(self.h_size, self.h_size)
        self.close_button.setStyleSheet("background-color: green;")
        self.close_button.setAlignment(Qt.AlignmentFlag.AlignCenter|Qt.AlignmentFlag.AlignCenter)
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
            self._window_normal_size = self.window_instance.frameGeometry()
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


    # def mouseMoveEvent(self, event):
    #     if (event.buttons() == Qt.LeftButton) and (self.title_label.geometry().contains(event.position().toPoint())):  # Updated this line
    #         if self.window_instance.isMaximized():
    #             self.window_instance.showNormal()

    #             topbar_middle = QPoint(self.window_instance.width()/2, self.height()/2)
    #             diff = event.globalPosition().toPoint() - QPoint(self.window_instance.width()/2, self.height()/2)
    #             self.window().move(self.window().pos() + diff)
    #             self.start_move_pos = event.globalPosition().toPoint()
    #             event.accept()
    #         else:
    #             diff = event.globalPosition().toPoint() - self.start_move_pos
    #             self.window().move(self.window().pos() + diff)
    #             self.start_move_pos = event.globalPosition().toPoint()
    #             event.accept()


    def mouseMoveEvent(self, event):
        if (event.buttons() == Qt.LeftButton) and (self.title_label.geometry().contains(event.position().toPoint())):

            # If the window is maximized, return to normal and adjust position
            if self.window_instance.isMaximized():
                cursor_global_pos = event.globalPosition().toPoint()
                self.window_instance.showNormal()

                # x = cursor_global_pos.x() - self._window_normal_size.width() / 2
                x = cursor_global_pos.x() - self.window_instance.getNormalSize.width() / 2
                y = cursor_global_pos.y() - self.title_label.height() / 2

                self.window_instance.move(x, y)
                self.start_move_pos = cursor_global_pos

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

        settings_icon = colorizeImage(QPixmap(os.path.join(DIR, 'assets', 'icons', 'icons8-settings-96.png')), QColor(206, 206, 206))
        settings_icon = resizeImage(settings_icon, icon_size)
        home_icon = colorizeImage(QPixmap(os.path.join(DIR, 'assets', 'icons', 'home.png')), QColor(206, 206, 206))
        home_icon = resizeImage(home_icon, icon_size)

        self.home_button = ClickableLabel()
        self.home_button.setFixedSize(size, size)
        self.home_button.setPixmap(home_icon)
        self.home_button.setHover()
        self.home_button.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignCenter)
        self.menu_layout.addWidget(self.home_button)

        self.settings_button = ClickableLabel()
        self.settings_button.setFixedSize(size, size)
        self.settings_button.setPixmap(settings_icon)
        self.settings_button.setHover()
        self.settings_button.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignCenter)
        self.menu_layout.addWidget(self.settings_button)



