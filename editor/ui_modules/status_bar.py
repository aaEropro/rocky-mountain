from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *


class ElidedLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)  # Start with fixed policy by default

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)

    def setText(self, text: str):
        super().setText(text)
        if text:
            # If there is text, make it expandable
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        else:
            # If there's no text, set to fixed
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def clear(self):
        super().clear()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)



class MessageLabelWithTimer(ElidedLabel):
    """
        a QLabel with the capacity to display a message for a sepcified time span.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = []
        self.infinit_timer_flag = False    # flag to inform that the current message has an infinit lifespan
        self.activ_timer_flag = False    # flag to inform that a timer is running

        self.timer = QTimer(self)    # create the timer that will track the lifespan of the messages displayed


    def changeHappened(self, timeout:bool=False):
        """ a change happened. it can be a new message has been added to queue, or a timer has expired. """
        if timeout:
            self.activ_timer_flag = False    # deactivate the flag
        
        if not self.activ_timer_flag:
            self.clear()    # clear the label from any messages
            if len(self.queue) > 0:
                self.showNextMessage()    # display the next message


    def addMessageToQueue(self, message:str, timer:int|None, override:bool=False):
        """ add a mesage to the queue. it the timer is None, it creates a message with an inifnit lifespan. """
        if not self.infinit_timer_flag:    # not inifnit timespan message displayed or an override
            self.queue.append( (message, timer) )    # append the message to queue
            self.changeHappened()    # indicate a change happened
        elif override:
            self.queue.append( (message, timer) )    # append the message to queue
            self.changeHappened(True)    # indicate a change happened


    def showNextMessage(self):
        """" displayes the next message in the queue. """
        message, timer = self.queue[0]    # unpack the first message
        self.setText(str(message))    # display the message
        if timer is not None:
            self.timer.singleShot(int(timer), lambda: self.changeHappened(True))    # start single shot timer
            self.activ_timer_flag = True    # set the flag to indicate an activ timer
        else:
            self.infinit_timer_flag = True    # set the flag to indicate an infinit lifespan message
        self.queue.pop(0)    # remove the displayed message from the queue





class StatusBar(QWidget):
    """
        a reimplementation of the QStatusBar.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_layout = QHBoxLayout(self)    # create a new layout
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # remove margins if desired
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)    # set the new layout

        self.left_label = MessageLabelWithTimer(self)
        self.left_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # self.left_label.setStyleSheet('''background:red''')
        self.center_label = MessageLabelWithTimer(self)
        self.center_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        # self.center_label.setStyleSheet('''background:green''')
        self.right_label = MessageLabelWithTimer(self)
        self.right_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # self.right_label.setStyleSheet('''background:blue''')

        self.main_layout.addWidget(self.left_label)
        self.main_layout.addWidget(self.center_label)
        self.main_layout.addWidget(self.right_label)

        self.setFixedHeight(25)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)


    @Slot(str, object)
    def showLeftMessage(self, message:str, timer:int|None=5000, override:bool=False):
        self.left_label.addMessageToQueue(message, timer, override)


    @Slot(str, object)
    def showCenterMessage(self, message:str, timer:int|None=5000, override:bool=False):
        self.center_label.addMessageToQueue(message, timer, override)


    @Slot(str, object)
    def showRightMessage(self, message:str, timer:int|None=5000, override:bool=False):
        self.right_label.addMessageToQueue(message, timer, override)