from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import warnings
from editor.data_modules.book_master import BookMaster
import os
from configobj import ConfigObj
from editor.ui_modules.buttons_bar import ButtonsBar
from editor.ui_modules.book_editor import BookEditor
from editor.ui_modules.book_navigation import BookNavigation
from editor.ui_modules.settings import SettingsWidget
from functools import partial
from addons import cutils
from editor.data_modules.autosave import AutoSave
from editor.ui_modules.status_bar import StatusBar
warnings.filterwarnings("ignore", category=DeprecationWarning)




class EditorWindow(QStackedWidget):

    bookmaster = None

    previous_split = None
    next_split = None

    chapter_buttons_always_show = False

################################## SETUP ##########################################################
    def __init__(self):
        '''
            initialization with minimum of separate module loading.

            for proper setup, it requires calling the 'activate' function.
        '''
        super().__init__()

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
        # self.buttons_bar.reload_btn.clicked.connect(lambda: self.loadTextToEditor(self.split_filename, self.editor.textCursor().position()))
        self.buttons_bar.reload_btn.clicked.connect(self.editor.reloadCurrentText)
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


    def loadSetupData(self) -> None:    # load the setting for the app from the last time it was used
        setup = ConfigObj(os.path.join('editor', 'setup_files', 'setup.ini'))

        self.chapter_buttons_always_show = cutils.isbool(setup['settings']['chapter_buttons_always_show'])
        
        if setup['misc']['read-only'] == 'True':    # set read-only button settings
            self.buttons_bar.toggle_readonly_btn.click()


    def activate(self, book:str) -> None:
        ''' activate the editor by loading a book. 'book' is the path to the .rmb file.'''
        self.bookmaster = BookMaster(book)    # initiate the bookmaster
        self.editor.setBookmaster(self.bookmaster)

        cursor_position, split_filename = self.bookmaster.getStartpoint()
        self.loadTextToEditor(split_filename, cursor_position)


################################## BOOK NAVIGATION ################################################
    def switchToBookNavigationPage(self) -> None:
        book_navigation = BookNavigation(self.bookmaster)    # initiate book navigation
        book_navigation.load_specific_split_signal.connect(self.loadTextToEditor)
        book_navigation.exit_navigation_signal.connect(self.exitBookNavigationPage)
        self.addWidget(book_navigation)
        self.setCurrentIndex(1)    # bring the book navigation page to the top


    def exitBookNavigationPage(self, navigation_obj:object) -> None:
        if not self.bookmaster.splitExists(self.split_filename):    # verify if the old split has been deleted
            first_available_split = self.bookmaster.getSplitByIndex(0)
            if first_available_split is not None:    # get the first split available
                self.loadTextToEditor(first_available_split)    # load the first available split
            else:
                raise FileNotFoundError('no split could be supplied')
        self.checkScrollPosition()    # force a check on the prev/next buttons
        self.switchToEditor(navigation_obj)    # switch to the editorer page


################################## SETTINGS #######################################################
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
        self.switchToEditor(settings_obj)


################################## EDITOR #########################################################
    def switchToEditor(self, widget_from_previous_editor:QWidget) -> None:
        ''' switches to the editor page. '''
        self.removeWidget(widget_from_previous_editor)
        widget_from_previous_editor.deleteLater()    # marks the previous page for deletion
        self.setCurrentIndex(0)    # force the stack widget to return to the editorer page.
                                   # if there is no other page it automatically does so, 
                                   # so this is a failsafe


    def loadTextToEditor(self, split_name:str = None, cursor_position:int=0):
        ''' loads the text to the editor. '''
        self.split_filename = split_name    # update the split name

        self.bookmaster.setCurrentSplit(self.split_filename)    # update the bookmaster's curent split
        contents = self.bookmaster.getContentsOfSplit(self.split_filename)
        self.editor.setTextContents(contents, cursor_position)

        self.status_bar.showLeftMessage(self.split_filename, timer=None, override=True)

        self.checkScrollPosition()    # force a check on the prev/next buttons
        self.editor.setFocus()


    def checkScrollPosition(self) -> None:
        ''' checks to see if the prev/next chapter buttons can lead to a valid split. '''
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


################################## EXIT ###########################################################
    def closeEventHandle(self) -> None:
        ''' handles the saves before closing the app. '''
        if self.bookmaster is not None:    # check if a book was opened
            self.bookmaster.write(self.split_filename, self.editor.toPlainText())
            cursor = self.editor.textCursor()
            self.bookmaster.close(cursor.position(), self.split_filename)     # save the position and split

        setup = ConfigObj(os.path.join('editor', 'setup_files', 'setup.ini'))
        setup['settings']['chapter_buttons_always_show'] = self.chapter_buttons_always_show
        setup['misc']['read-only'] = self.buttons_bar.toggle_readonly_btn.isChecked()
        setup.write()