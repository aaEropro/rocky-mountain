from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys
from editor.main import EditorWindow



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.editor_window = EditorWindow(self)
        self.setCentralWidget(self.editor_window)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    instance = MainWindow()
    instance.show()
    sys.exit(app.exec())