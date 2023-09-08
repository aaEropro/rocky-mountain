from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys
import os

from src.explorer.ui.display_case import DisplayCase
from src.explorer.data.library_master import LibraryMasterStn
from addons.flowing_scroll import ResizeScrollArea
from src.settings.data.settings_master import SettingsMasterStn
from src.explorer.ui.hires_cover_viewer import HighResViewer



class ExplorerWindow(QWidget):
    def __init__(self, return_commnd) -> None:
        super().__init__()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 2, 0, 0)

        self.covers_list = LibraryMasterStn().getCoversData()

        self.scroll_area = ResizeScrollArea(self)
        self.scroll_area.setWidgetResizable(True)    # let the scroll area resize its child
        self.main_layout.addWidget(self.scroll_area)

        self.display_case = DisplayCase(self)
        self.display_case.setBooks(self.covers_list)
        self.display_case.setReturnCommand(return_commnd)
        self.display_case.right_click.connect(self.createHighresViewer)
        self.scroll_area.setWidget(self.display_case)


################################## HIGHRES VIEWER #################################################
    def createHighresViewer(self, bookname:str):
        cover_name = LibraryMasterStn().getBookCover(bookname)
        library_path = SettingsMasterStn().getSpecific('library-path')
        cover_path = os.path.join(library_path, 'cache', cover_name)

        highres_viewer = HighResViewer(self, cover_path)
        highres_viewer.show()
        highres_viewer.setFocus()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.resize(600, 600)
   
    instance = ExplorerWindow(print, 'library')

    window.setCentralWidget(instance)

    window.show()
    sys.exit(app.exec())