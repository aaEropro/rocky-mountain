from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from functools import partial
from addons.overlay import OverlayWidget


class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.default_stylesheet =   '''
                                        QLabel {
                                            background-color: rgb(42, 41, 41);
                                            color: rgb(190, 189, 189);
                                            border: none;
                                        }
                                    '''
        
        self.clicked_stylesheet =   '''
                                        QLabel {
                                            border: none;
                                        }
                                    '''
        self.setStyleSheet(self.default_stylesheet)
    
        self.click = False
        self.has_exit = False

    def setCurrent(self) -> None:
        print(f'current {self.text()}')
        self.default_stylesheet =   '''
                                QLabel {
                                    background-color: rgba(0, 0, 255, 0.1);
                                    color: rgb(190, 189, 189);
                                    border: none;
                                }
                            '''
        self.setStyleSheet(self.default_stylesheet)

    def setHover(self):
        self.setStyleSheet('QLabel:hover {background-color: rgb(70, 69, 69);}')
        
    def mousePressEvent(self, event:QMouseEvent) -> None:
        ''' manages mouse press. '''
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.clicked_stylesheet)
            self.click = True
            self.has_exit = False
    
        return True
    

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        ''' handle the mouse exiting the QFrame. '''
        main_geometry = self.rect()
        event_in_main_geometry = main_geometry.contains(event.pos())

        if self.click and (not event_in_main_geometry) and (not self.has_exit):
            self.setStyleSheet(self.default_stylesheet)
            self.has_exit = True
        
        elif self.click and event_in_main_geometry and self.has_exit:
            self.setStyleSheet(self.clicked_stylesheet)
            self.has_exit = False

        return super().mouseMoveEvent(event)
    

    def mouseReleaseEvent(self, event:QMouseEvent) -> None:
        ''' manages mouse release. '''
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.default_stylesheet)
            self.click = False
            if not self.has_exit:
                self.clicked.emit()
            self.has_exit = False

        return True
    
class ClickableLabel2(QLabel):
    clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.default_stylesheet =   '''
                                        QLabel {
                                            background-color: rgb(27, 27, 27);
                                            color: rgb(190, 189, 189);
                                            border: none;
                                        }
                                    '''
        
        self.clicked_stylesheet =   '''
                                        QLabel {
                                            border: none;
                                        }
                                    '''
        self.setStyleSheet(self.default_stylesheet)
    
        self.click = False
        self.has_exit = False

    def setCurrent(self) -> None:
        print(f'current {self.text()}')
        self.default_stylesheet =   '''
                                QLabel {
                                    background-color: rgba(0, 0, 255, 0.1);
                                    color: rgb(190, 189, 189);
                                    border: none;
                                }
                            '''
        self.setStyleSheet(self.default_stylesheet)

    def setHover(self):
        self.setStyleSheet('QLabel:hover {background-color: rgb(70, 69, 69);}')
        
    def mousePressEvent(self, event:QMouseEvent) -> None:
        ''' manages mouse press. '''
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.clicked_stylesheet)
            self.click = True
            self.has_exit = False
    
        return True
    

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        ''' handle the mouse exiting the QFrame. '''
        main_geometry = self.rect()
        event_in_main_geometry = main_geometry.contains(event.pos())

        if self.click and (not event_in_main_geometry) and (not self.has_exit):
            self.setStyleSheet(self.default_stylesheet)
            self.has_exit = True
        
        elif self.click and event_in_main_geometry and self.has_exit:
            self.setStyleSheet(self.clicked_stylesheet)
            self.has_exit = False

        return super().mouseMoveEvent(event)
    

    def mouseReleaseEvent(self, event:QMouseEvent) -> None:
        ''' manages mouse release. '''
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.default_stylesheet)
            self.click = False
            if not self.has_exit:
                self.clicked.emit()
            self.has_exit = False

        return True


class CScrollArea(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)

        self._start_touch_point = QPoint()

    def event(self, event:QEvent):    # event filter for touch
        ''' add custome behaviour for touch events. '''

        if event.type() == QTouchEvent.TouchBegin:
            self._start_touch_point = event.touchPoints()[0].startPos().y()
            return True

        elif event.type() == QTouchEvent.TouchUpdate and self._start_touch_point is not None:
            delta = event.touchPoints()[0].pos().y() - self._start_touch_point
            self._start_touch_point = event.touchPoints()[0].pos().y()
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta)
            return True

        elif event.type() == QTouchEvent.TouchEnd:
            self._start_touch_point = None
            return True

        return super().event(event)


class BookNavigation(OverlayWidget):
    exit = Signal(object, object)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.master_layout = QVBoxLayout(self)
        self.master_layout.setContentsMargins(0, 0, 0, 0)

        self.container_widget = QWidget(self)
        self.container_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.container_widget.setStyleSheet("""
                                            QWidget {
                                                border: 1px solid white;
                                                background: rgb(42, 41, 41);
                                            }
                                            QScrollArea {
                                                border: none;
                                            }
                                            ClickableLabel2 {
                                                border: none
                                            }
                                        """)
        self.master_layout.addWidget(self.container_widget, alignment=Qt.AlignmentFlag.AlignRight)
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setSpacing(0)

        self.exit_button = ClickableLabel2(self.container_widget)
        self.exit_button.setText('exit')
        self.exit_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exit_button.setHover()
        self.exit_button.setMargin(7)
        self.exit_button.clicked.connect(lambda: self.exit.emit(self, None))
        self.container_layout.addWidget(self.exit_button)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setContentsMargins(20, 20, 20, 20)
        self.container_layout.addWidget(self.scroll_area)
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet('border:none')
        self.scroll_area.setWidget(self.content_widget)
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)


    def loadChapters(self, chapters:list, current:str|None):
        self.chapter_dict = {}
        for item in chapters:
            obj = ClickableLabel(self.content_widget)
            obj.setText(item)
            obj.setHover()
            obj.setContentsMargins(15, 5, 15, 5)
            obj.clicked.connect(partial(self.exit.emit, self, item))
            self.content_layout.addWidget(obj)
            self.chapter_dict[item] = obj

            if item == current:
                obj.setCurrent()