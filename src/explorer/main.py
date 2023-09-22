from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys
import os

from src.explorer.ui.display_case import DisplayCase
from addons.flowing_scroll import ResizeScrollArea
from src.settings.data.settings_master import SettingsMasterStn
from src.explorer.ui.hires_cover_viewer import HighResViewer
from src.explorer.data.library_master_2 import LibraryMaster



class ExplorerWindow(QWidget):
    clicked = Signal(str)
    library_path = None

    def __init__(self) -> None:
        super().__init__()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 2, 0, 0)

        self.scroll_area = ResizeScrollArea(self)
        self.scroll_area.setWidgetResizable(True)    # let the scroll area resize its child
        self.main_layout.addWidget(self.scroll_area)

        self.display_case = DisplayCase(self)
        self.display_case.select_library_path.connect(self.selectPath)
        self.scroll_area.setWidget(self.display_case)

        self.loadLibMaster(SettingsMasterStn().getSpecific('library-path'))


    def selectPath(self):
        ''' open a file dialog to select a directory. '''
        folder_name = QFileDialog.getExistingDirectory(None, "Select Folder")
        if folder_name:
            SettingsMasterStn().setSpecific('library-path', folder_name)
            self.loadLibMaster(folder_name)


    def loadLibMaster(self, path):
        ''' create the library master if the path is valid. '''
        if not os.path.isdir(path):
            return
        
        self.library_path = path
        self.library_master = LibraryMaster(self.library_path)
        self.covers_list = self.library_master.getCoversData()

        self.display_case.setBooks(self.covers_list)
        self.display_case.left_click.connect(self.clicked.emit)
        self.display_case.right_click.connect(self.createHighresViewer)


################################## HIGHRES VIEWER #################################################
    def createHighresViewer(self, bookname:str):
        ''' creates an overlay for highres viewing of the cover. '''
        cover_name = self.library_master.getBookCover(bookname)
        cover_path = os.path.join(self.library_path, 'cache', cover_name)

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