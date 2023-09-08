from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys
import os

from src.editor.main import EditorWindow
from src.explorer.main import ExplorerWindow
from addons.main_window import MainWindow
from addons.title_bar import TitleBar
from src.settings.ui.settings_ui import Settings
from src.settings.data.settings_master import SettingsMasterStn
from src.explorer.data.library_master import LibraryMasterStn

import ctypes
myappid = u'tryhardCo.stupidAsAlways.RockyMountain.0'    # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

VERSION = '0.2.0'


class MainWindow(MainWindow):
    def __init__(self):
        super().__init__()

        self.atCreation()

        self.current_widget = None

        with open('dark_mode.css') as file:
            self.editor_window_dark_mode_styling = file.read()
        self.setStyleSheet(self.editor_window_dark_mode_styling)

        self.title_bar = TitleBar()
        self.title_bar.setWindowInstance(self)
        self.title_bar.setTitle(f'Rocky Mountain - {VERSION}')
        self.title_bar.settings_button.clicked.connect(self.createSettingsPage)
        self.title_bar.home_button.clicked.connect(self.goHome)
        self.setTitleBar(self.title_bar)

        self.central_widget = QStackedWidget(self)
        self.central_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.central_widget)
        
        self.explorer_window = ExplorerWindow(self.loadBook)
        self.explorer_window.display_case.left_click.connect(self.loadBook)
        self.central_widget.addWidget(self.explorer_window)
        self.current_widget = self.explorer_window

        self.createEditorWidget()


    def createEditorWidget(self) -> None:
        self.editor_window = EditorWindow()
        self.central_widget.addWidget(self.editor_window)


    def loadBook(self, bookname:str) -> None:
        self.editor_window.activate(os.path.join(SettingsMasterStn().getSpecific('library-path'), bookname))

        self.central_widget.setCurrentWidget(self.editor_window)
        self.current_widget = self.editor_window

        author = LibraryMasterStn().getBookAuthor(bookname[:-4])
        title = LibraryMasterStn().getBookTitle(bookname[:-4])
        self.title_bar.setTitle(f'{author[0]} {author[1]}: {title}')


################################## SETTINGS #######################################################
    def createSettingsPage(self):
        settings_page = Settings()
        settings_page.exit_pipeline.connect(self.exitSettingsPage)
        self.central_widget.addWidget(settings_page)
        self.central_widget.setCurrentWidget(settings_page)


    def exitSettingsPage(self, settings_instance:QWidget):
        self.central_widget.removeWidget(settings_instance)
        self.central_widget.setCurrentWidget(self.current_widget)
        settings_instance.close()
        settings_instance.deleteLater()

################################## HOME ###########################################################
    def goHome(self):
        self.editor_window.close()
        self.editor_window.deleteLater()
        self.createEditorWidget()
        self.central_widget.setCurrentWidget(self.explorer_window)


##################################  #####################################################
    def atCreation(self):
        window_width, window_height = SettingsMasterStn().getSpecific('window-resolution')
        window_pos_x, window_pos_y = SettingsMasterStn().getSpecific('window-position')
        window_width = int(window_width); window_height = int(window_height)
        window_pos_x = int(window_pos_x); window_pos_y = int(window_pos_y)

        if window_pos_x < 0: window_pos_x = 0    # check the window position to not be outside the screen
        if window_pos_y < 0: window_pos_y = 0

        self.resize(window_width, window_height)    # resize the window
        self.move(window_pos_x, window_pos_y)    # move the window to the desired location


    def closeEvent(self, event: QCloseEvent) -> None:
        window_size = (self.size().width(), self.size().height())        # get window size
        window_position = (self.pos().x(), self.pos().y())     # get window position
        
        SettingsMasterStn().setSpecific(topic='window-resolution', value=window_size)
        SettingsMasterStn().setSpecific(topic='window-position', value=window_position)

        return super().closeEvent(event)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    instance = MainWindow()
    icon = QIcon(os.path.join('assets', 'logos', 'rm_logo.ico'))
    app.setWindowIcon(icon)
    instance.show()
    sys.exit(app.exec())