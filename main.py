from PySide6.QtCore import *
from PySide6.QtGui import *
import PySide6.QtGui
from PySide6.QtWidgets import *
import sys
from editor.main import EditorWindow
from explorer.main import ExplorerWindow
import os
from configobj import ConfigObj


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        with open(os.path.join('editor', 'setup_files', 'editor_window_dark_mode.css')) as file:
            self.editor_window_dark_mode_styling = file.read()
        self.setStyleSheet(self.editor_window_dark_mode_styling)

        self.central_widget = QStackedWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.explorer_window = ExplorerWindow(self.loadBook, 'library')
        self.central_widget.addWidget(self.explorer_window)

        self.editor_window = EditorWindow()
        self.central_widget.addWidget(self.editor_window)

        self.loadSetupData()

    
    def loadBook(self, bookname:str) -> None:
        self.editor_window.activate(os.path.join('library', bookname))
        self.central_widget.setCurrentWidget(self.editor_window)


    def closeEvent(self, event: QCloseEvent) -> None:
        self.editor_window.closeEventHandle()

        window_size = self.size()        # get window size
        window_position = self.pos()     # get window position
        setup = ConfigObj(os.path.join('editor', 'setup_files', 'setup.ini'))
        setup['window']['resolution'] = (window_size.width(), window_size.height())
        setup['window']['position'] = (window_position.x(), window_position.y())
        setup.write()

        return super().closeEvent(event)
    

    def loadSetupData(self):
        setup = ConfigObj(os.path.join('editor', 'setup_files', 'setup.ini'))
        window_size = list(int(x) for x in setup['window']['resolution'])    # convert the str values to int
        window_position = list(int(x) for x in setup['window']['position'])

        if window_position[0] < 0: window_position[0] = 0    # check the window position to not be 
        if window_position[1] < 0: window_position[1] = 0    # outside the screen
        self.resize(window_size[0], window_size[1])    # resize the window
        self.move(window_position[0], window_position[1])    # move the window to the desired location



if __name__ == '__main__':
    app = QApplication(sys.argv)
    instance = MainWindow()
    instance.show()
    sys.exit(app.exec())