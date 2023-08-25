from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys




class OverflowControl(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(OverflowControl, self).__init__(*args, **kwargs)
        self.full_text = ""

    def uploadFromFile(self, path:str, cursor_position:int = 0) -> None:
        # with open(path, encoding= 'utf-8', mode='r') as file:    # read the respective file
        #     self.full_text = file.read()
        self.full_text = "Your long text goes here.\n" * 50
        self.loadControl()

    def loadControl(self):
        self.clear()
        
        lines = self.full_text.splitlines()
        for line in lines:
            self.append(line)
            
            # Check if content overflows
            if self.verticalScrollBar().maximum() > 0:
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.PreviousBlock, QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                break

    def resizeEvent(self, event):
        super(OverflowControl, self).resizeEvent(event)
        self.loadControl()