from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys
import warnings
from editor.data_modules.book_master import BookMaster
from pathlib import Path
import os
from configobj import ConfigObj
from editor.ui_modules.buttons_bar import ButtonsBar
from editor.ui_modules.book_editor import BookEditor
from editor.ui_modules.book_navigation import BookNavigation
from editor.ui_modules.settings import SettingsWidget
from functools import partial
from addons import cutils
from editor.data_modules.autosave_thread import AutoSave
from editor.ui_modules.status_bar import StatusBar
warnings.filterwarnings("ignore", category=DeprecationWarning)

class EditorWindow(QStackedWidget):

    bookmaster = None
    rmb_filename = None

    previous_split = None
    next_split = None

    chapter_buttons_always_show = False

    def __init__(self):
        super().__init__()

        # self.stacked_widget = QStackedWidget()

        self.widget1 = QWidget()
        self.widget1.setLayout(QVBoxLayout())
        self.addWidget(self.widget1)

        #: buttons
        self.buttons_bar = ButtonsBar(self.widget1)
        self.buttons_bar.move_to_previous_chapter_btn.clicked.connect(lambda: self.loadTextToEditor(self.previous_split))
        self.buttons_bar.move_to_next_chapter_btn.clicked.connect(lambda: self.loadTextToEditor(self.next_split))
        self.widget1.layout().addWidget(self.buttons_bar)

        #: editor
        self.editor = BookEditor(self.widget1)
        self.widget1.layout().addWidget(self.editor)
        self.editor.verticalScrollBar().valueChanged.connect(self.checkScrollPosition)
        self.buttons_bar.navigate_btn.clicked.connect(self.switchToBookNavigationPage)
        self.buttons_bar.reload_btn.clicked.connect(lambda: self.loadTextToEditor(self.split_filename, self.editor.textCursor().position()))
        self.buttons_bar.settings_btn.clicked.connect(self.switchToSettingsPage)
        self.buttons_bar.toggle_readonly_btn.clicked.connect(lambda: self.editor.toggleReadOnly(self.buttons_bar.toggle_readonly_btn))
        self.buttons_bar.toggle_context_help_btn.clicked.connect(lambda: self.editor.toggleContextHelp(self.buttons_bar.toggle_context_help_btn))
        self.buttons_bar.toggle_tabletmode_btn.clicked.connect(lambda: self.editor.toggleTabletMode(self.buttons_bar.toggle_tabletmode_btn))

        self.autosave = AutoSave(self.editor)
        self.editor.setAutoSave(self.autosave)

        self.status_bar = StatusBar(self)
        self.widget1.layout().addWidget(self.status_bar)
        self.autosave.print_message_to_status_bar.connect(self.status_bar.showRightMessage)

        self.loadSetupData()


    def activate(self, book:str) -> None:
        self.bookmaster = BookMaster(book)    # initiate the bookmaster
        self.rmb_filename = self.bookmaster.getArchiveName()      # get the file's name
        self.editor.setBookmaster(self.bookmaster)

        cursor_position, split_filename = self.bookmaster.getStartpoint()
        self.loadTextToEditor(split_filename, cursor_position)


    def switchToBookNavigationPage(self) -> None:
        book_navigation = BookNavigation(self.bookmaster)    # initiate book navigation
        # book_navigation.load_specific_split_signal.connect(self.laterLoad)
        book_navigation.load_specific_split_signal.connect(self.loadTextToEditor)
        book_navigation.exit_navigation_signal.connect(self.exitBookNavigationPage)
        self.addWidget(book_navigation)
        self.setCurrentIndex(1)    # bring the book navigation page to the top


    def exitBookNavigationPage(self, navigation_obj:object) -> None:
        if not self.bookmaster.splitExists(self.split_filename):    # verify if the old split has been deleted
            first_available_split = self.bookmaster.getSplitByIndex(0)
            if first_available_split is not None:    # get the first split available
                # self.laterLoad(first_available_split)    # load the first available split
                self.loadTextToEditor(first_available_split)    # load the first available split
            else:
                raise FileNotFoundError('no split could be supplied')
        self.checkScrollPosition()    # force a check on the prev/next buttons
        self.switchToeditorer(navigation_obj)    # switch to the editorer page


    def switchToSettingsPage(self) -> None:
        settings = SettingsWidget()
        settings.exit_settings_signal.connect(self.exitSettingsPage)
        settings.loadSettings({'chapter_buttons_always_show': self.chapter_buttons_always_show})
        self.addWidget(settings)
        self.setCurrentIndex(1)    # bring the settings page to the top


    def exitSettingsPage(self, settings_obj:object, settings_dict:dict) -> None:
        for key, value in settings_dict.items():
            if hasattr(self, key):  # check if the attribute exists
                setattr(self, key, value)
        self.checkScrollPosition()    # force a check on the prev/next buttons
        self.switchToeditorer(settings_obj)


    def switchToEditor(self, widget_from_previous_editor) -> None:
        self.removeWidget(widget_from_previous_editor)
        widget_from_previous_editor.deleteLater()    # marks the previous page for deleteon
        self.setCurrentIndex(0)    # force the stack widget to return to the editorer page.
                                                  # if there is no other page it automatically does so, 
                                                  # so this is a failsafe


    def loadSetupData(self) -> None:    # load the setting for the app from the last time it was used
        setup = ConfigObj(os.path.join('editor', 'setup_files', 'setup.ini'))
        window_size = list(int(x) for x in setup['window']['resolution'])    # convert the str values to int
        window_position = list(int(x) for x in setup['window']['position'])

        if window_position[0] < 0: window_position[0] = 0    # check the window position to not be 
        if window_position[1] < 0: window_position[1] = 0    # outside the screen
        self.resize(window_size[0], window_size[1])    # resize the window
        self.move(window_position[0], window_position[1])    # move the window to the desired location

        self.chapter_buttons_always_show = cutils.isbool(setup['settings']['chapter_buttons_always_show'])
        
        if setup['misc']['read-only'] == 'True':    # set read-only button settings
            self.buttons_bar.toggle_readonly_btn.click()


    def loadTextToEditor(self, split_name:str = None, cursor_position:int=0):
        self.split_filename = split_name    # update the split name

        self.bookmaster.setCurrentSplit(self.split_filename)    # update the bookmaster's curent split
        contents = self.bookmaster.getContentsOfSplit(self.split_filename)
        self.editor.setTextContents(contents, cursor_position)

        self.status_bar.showLeftMessage(self.split_filename, timer=None, override=True)

        self.checkScrollPosition()    # force a check on the prev/next buttons
        self.editor.setFocus()


    def checkScrollPosition(self) -> None:
        if self.bookmaster is not None:     # the bookmaster is created on initial load, so this bypasses 
                                            # the check during the editorer widget's placement

            self.previous_split = self.bookmaster.getPrevSplit(self.split_filename)    # update the previous split
            self.next_split = self.bookmaster.getNextSplit(self.split_filename)    # update the next split

            scrollbar = self.editor.verticalScrollBar()
            value = scrollbar.value()    # get the value of the scrollbar

            self.buttons_bar.move_to_previous_chapter_btn.hide()
            self.buttons_bar.move_to_next_chapter_btn.hide()

            if (value == scrollbar.minimum()) or (self.chapter_buttons_always_show):    # the displayed text is scrolled to the top or the buttons are forced
                if self.previous_split is not None:
                    self.buttons_bar.move_to_previous_chapter_btn.show()

            if (value == scrollbar.maximum()) or (self.chapter_buttons_always_show):    # the displayed text is scrolled to the bottom or the buttons are forced.
                if self.next_split is not None:                                         # if the text doesn't require scrolling, the value
                    self.buttons_bar.move_to_next_chapter_btn.show()                    # will be equal to both minimum and maximum.



    def closeEvent(self, event):
        if self.bookmaster is not None:    # check if a book was opened
            self.bookmaster.write(self.split_filename, self.editor.toPlainText())
            cursor = self.editor.textCursor()
            self.bookmaster.close(cursor.position(), self.split_filename)     # save the position and split

        window_size = self.size()        # get window size
        window_position = self.pos()     # get window position

        setup = ConfigObj(os.path.join('editor', 'setup_files', 'setup.ini'))
        setup['window']['resolution'] = (window_size.width(), window_size.height())
        setup['window']['position'] = (window_position.x(), window_position.y())
        setup['settings']['chapter_buttons_always_show'] = self.chapter_buttons_always_show
        setup['misc']['read-only'] = self.buttons_bar.toggle_readonly_btn.isChecked()
        setup.write()

        super().closeEvent(event)   # close the app