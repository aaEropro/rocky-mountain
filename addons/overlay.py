from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QWidget


class OverlayWidget(QWidget):
    '''
        A class that extends QWidget and adds the capability to set an overlay on another widget.
    '''

    def __init__(self, parent:QObject, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent().installEventFilter(self)
        self.setStyleSheet('background: transparent')
        self.resize(self.parent().size())


    def closeOverlay(self):
        ''' triggers the event filter removal and the removal of the overlay. '''

        self.parent().removeEventFilter(self)
        self.close()
        self.deleteLater()


    def eventFilter(self, object:QObject, event:QEvent) -> bool:
        ''' catches the events to the parent and listens for a resize event. '''

        if object == self.parent() and isinstance(event, QResizeEvent):    # the widget under the overlay is being resized
            self.resize(object.size())    # resize the overlay
            return False    # allow the widget underneath to be resized
        return super().eventFilter(object, event)