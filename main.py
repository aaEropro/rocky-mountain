from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys
from editor.main import EditorWindow
from explorer.main import ExplorerWindow
import os
from configobj import ConfigObj
from addons.main_window import MainWindow
from addons.title_bar import TitleBar
from settings import Settings

import ctypes
myappid = u'tryhardCo.stupidAsAlways.RockyMountain.0'    # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

VERSION = '0.1.3'


class MainWindow(MainWindow):
    def __init__(self):
        super().__init__()

        self.current_page = None
        self.settings = {
            'cover_constraint': [225, 225] 
        }

        with open(os.path.join('editor', 'setup_files', 'editor_window_dark_mode.css')) as file:
            self.editor_window_dark_mode_styling = file.read()
        self.setStyleSheet(self.editor_window_dark_mode_styling)

        self.title_bar = TitleBar()
        self.title_bar.setWindowInstance(self)
        self.title_bar.setTitle('window1')
        self.title_bar.settings_button.clicked.connect(self.createSettingsPage)
        self.setTitleBar(self.title_bar)

        self.central_widget = QStackedWidget(self)
        self.central_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.central_widget)
        
        self.explorer_window = ExplorerWindow(self.loadBook)
        self.central_widget.addWidget(self.explorer_window)
        self.current_page = self.explorer_window

        self.editor_window = EditorWindow()
        self.central_widget.addWidget(self.editor_window)

        self.loadSetupData()

    
    def loadBook(self, bookname:str) -> None:
        self.editor_window.activate(os.path.join(self.explorer_window.library_master.getLibraryPath(), bookname))
        self.central_widget.setCurrentWidget(self.editor_window)
        self.current_page = self.editor_window
        author = self.explorer_window.library_master.getBookAuthor(bookname[:-4])
        title = self.explorer_window.library_master.getBookTitle(bookname[:-4])
        self.title_bar.setTitle(f'{author[0]} {author[1]}: {title}')


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

        if window_position[0] < 0: window_position[0] = 0    # check the window position to not be outside the screen
        if window_position[1] < 0: window_position[1] = 0

        self.resize(window_size[0], window_size[1])    # resize the window
        self.move(window_position[0], window_position[1])    # move the window to the desired location


################################## SETTINGS #######################################################
    def createSettingsPage(self):
        settings_page = Settings(settings=self.settings)
        settings_page.exit_pipeline.connect(self.exitSettingsPage)
        self.central_widget.addWidget(settings_page)
        self.central_widget.setCurrentWidget(settings_page)


    def exitSettingsPage(self, settings_instance:QWidget, type:str, data:object):
        self.central_widget.removeWidget(settings_instance)
        self.central_widget.setCurrentWidget(self.current_page)
        settings_instance.close()
        settings_instance.deleteLater()
        if type == 'save':
            self.processChanges(data)


    def processChanges(self, data:dict):
        print('dda', data, self.settings)
        # for item in self.settings.keys():
        #     print(item)
        #     old_setting = self.settings[item]
        #     new_setting = data.get(item, '')
        #     print(old_setting, new_setting)
        #     if new_setting != old_setting:
        #         print('new')
        #         self.settings[item] = new_setting
        #         if item == 'cover_constraint':
        #             print(self.settings[item])
        #             self.explorer_window.setCoversSizeConstraints(self.settings['cover_constraint'])




if __name__ == '__main__':
    app = QApplication(sys.argv)
    instance = MainWindow()
    icon = QIcon(os.path.join('logos', 'rm_logo.ico'))
    app.setWindowIcon(icon)
    instance.show()
    sys.exit(app.exec())