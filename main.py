from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys
from editor.main import EditorWindow
from explorer.main import ExplorerWindow
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QStackedWidget(self)
        
        self.explorer_window = ExplorerWindow(self.loadBook)
        self.central_widget.addWidget(self.explorer_window)
        self.editor_window = EditorWindow()
        self.central_widget.addWidget(self.editor_window)

        self.setCentralWidget(self.central_widget)

    
    def loadBook(self, bookname:str) -> None:
        self.editor_window.activate(os.path.join('library', bookname))
        self.central_widget.setCurrentWidget(self.editor_window)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    instance = MainWindow()
    instance.show()
    sys.exit(app.exec())