from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from addons.title_bar import TitleBar


'''
    some code parts have been taken from @musicamante from StackOverflow: https://stackoverflow.com/a/62812752.
'''



class SideGrip(QWidget):

    def __init__(self, parent, edge):
        super().__init__(parent)

        if edge == Qt.LeftEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resize_func = self.resizeLeft
        elif edge == Qt.TopEdge:
            self.setCursor(Qt.SizeVerCursor)
            self.resize_func = self.resizeTop
        elif edge == Qt.RightEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resize_func = self.resizeRight
        else:
            self.setCursor(Qt.SizeVerCursor)
            self.resize_func = self.resizeBottom
        self.mousePos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.position().toPoint() - self.mousePos
            self.resize_func(delta)

    def mouseReleaseEvent(self, event):
        self.mousePos = None





class MainWindow(QMainWindow):
    '''
        class that expands the QMainWindow, allowing you to request the instance with a sepcific name.
    '''

    _grip_size = 4
    _instances = {}    # dict of all instances, shared between all instances


    def __new__(cls, *args, window_name=None, **kwargs):
        if window_name in cls._instances:    # if an instance with the same name exists, return it rarther then create a new one
            return cls._instances[window_name]
        
        instance = super(MainWindow, cls).__new__(cls)
        cls._instances[window_name] = instance
        return instance


    @staticmethod
    def instance(window_name:str=None) -> QObject:
        ''' returns the class instance with that name if it exists, else None. '''
        return MainWindow._instances.get(window_name)


    def __init__(self, window_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setWindowFlags(Qt.FramelessWindowHint)

        self.window_name = window_name
        self.title_bar = None
        self.central_widget = None
        self.status_bar = None

        self.main_widget = QWidget(self)
        # self.main_widget.setStyleSheet('background:blue')
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_widget.setLayout(self.main_layout)
        super().setCentralWidget(self.main_widget)

        self.side_grips = [
            SideGrip(self, Qt.LeftEdge), 
            SideGrip(self, Qt.TopEdge), 
            SideGrip(self, Qt.RightEdge), 
            SideGrip(self, Qt.BottomEdge), 
        ]    # corner grips should be "on top" of everything, otherwise the side grips will take precedence on mouse events, 
             # so we are adding them *after*; alternatively, widget.raise_() can be used.

        self.corner_grips = [QSizeGrip(self) for i in range(4)]

    @property
    def gripSize(self):
        ''' returns the size of the grips. '''

        return self._grip_size


    def setGripSize(self, size):
        ''' sets the size of the grips. '''
    
        if size == self._grip_size:
            return
        self._grip_size = max(2, size)
        self.updateGrips()


    def updateGrips(self):
        ''' updates the grip sizes. '''

        self.setContentsMargins(*[self.gripSize] * 4)    # set the layout margins

        out_rect = self.rect()
        inner_rect = out_rect.adjusted(self.gripSize, self.gripSize, -self.gripSize, -self.gripSize)    # an "inner" rect used for reference 
                                                                                                   # to set the geometries of size grips

        self.corner_grips[0].setGeometry(QRect(out_rect.topLeft(), inner_rect.topLeft()))    # top left
        self.corner_grips[1].setGeometry(QRect(out_rect.topRight(), inner_rect.topRight()).normalized())    # top right
        self.corner_grips[2].setGeometry(QRect(inner_rect.bottomRight(), out_rect.bottomRight()))    # bottom right
        self.corner_grips[3].setGeometry(QRect(out_rect.bottomLeft(), inner_rect.bottomLeft()).normalized())    # bottom left

        self.side_grips[0].setGeometry(0, inner_rect.top(), self.gripSize, inner_rect.height())    # left edge
        self.side_grips[1].setGeometry(inner_rect.left(), 0, inner_rect.width(), self.gripSize)    # top edge
        self.side_grips[2].setGeometry(inner_rect.left() + inner_rect.width(), inner_rect.top(), self.gripSize, inner_rect.height())    # right edge
        self.side_grips[3].setGeometry(self.gripSize, inner_rect.top() + inner_rect.height(), inner_rect.width(), self.gripSize)    # bottom edge


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateGrips()


    def setTitleBar(self, widget:QWidget):
        """
            Replace the current title bar with the provided widget.
        """

        if self.title_bar is not None:
            self.main_layout.removeWidget(self.title_bar)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.title_bar = widget
        self.title_bar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # self.main_layout.insertWidget(0, self.title_bar, 1, Qt.AlignmentFlag.AlignTop)    # aligns well, but there are problems with the central widget
        self.main_layout.insertWidget(0, self.title_bar)


    def setCentralWidget(self, widget:QWidget):
        """
            Replace the current central widget with the provided widget.
        """
        if self.central_widget is not None:
            self.main_layout.removeWidget(self.central_widget)

        self.central_widget = widget
        self.central_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.main_layout.insertWidget(1, self.central_widget)


    def setStatusBar(self, widget:QWidget):
        """
            Replace the current status bar with the provided widget.
        """
        if self.status_bar is not None:
            self.main_layout.removeWidget(self.status_bar)

        self.status_bar = widget
        self.status_bar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.main_layout.addWidget(self.status_bar)
