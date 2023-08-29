from PySide6.QtCore import *
import PySide6.QtCore
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import PySide6.QtWidgets
from explorer.display_case import DisplayCase
from explorer.library_master import LibraryMaster
from addons.flowing_scroll import ResizeScrollArea
import sys

class ExplorerWindow(QWidget):
    def __init__(self, return_commnd, library:str) -> None:
        super().__init__()

        self.setLayout(QVBoxLayout(self))

        self.library_master = LibraryMaster(library)
        self.last_read = self.library_master.getLastReadBookAndCover()
        self.covers_list = self.library_master.getBooksAndCoversList()

        self.scroll_area = ResizeScrollArea(self)
        self.scroll_area.setWidgetResizable(True)  # Let the scroll area resize its child
        self.layout().addWidget(self.scroll_area)

        self.display_case = DisplayCase(self)
        self.display_case.setBooksDict({'last-read': self.last_read, 'others': self.covers_list})
        self.display_case.setReturnCommand(return_commnd)
        self.scroll_area.setWidget(self.display_case)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.resize(600, 600)
   
    instance = ExplorerWindow(print)

    window.setCentralWidget(instance)

    window.show()
    sys.exit(app.exec())