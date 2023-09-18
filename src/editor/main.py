from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import atexit

from addons import cutils
from src.settings.data.settings_master import SettingsMasterStn
from src.editor.data.book_master_3 import BookMaster

from src.editor.ui.book_editor import BookEditor
from src.editor.ui.status_bar import StatusBar
from src.editor.ui.buttons_bar import ButtonsBar
from src.editor.ui.chapter_navigation_3 import BookNavigation
from src.editor.ui.metadata_editor import MetadataEditor



class EditorWindow(QStackedWidget):

    def __init__(self):
        '''
            initialization with minimum of separate module loading.

            for proper setup, it requires calling the 'activate' function.
        '''
        super().__init__()
        atexit.register(self.atExit)

        self.always_show_chapter_buttons = cutils.bool(SettingsMasterStn().getSpecific('always-show-chapter-buttons'))

        self.master_widget = QWidget(self)
        self.addWidget(self.master_widget)
        self.master_layout = QVBoxLayout(self.master_widget)
        self.master_layout.setContentsMargins(0, 0, 0, 0)

        self.bookmaster = BookMaster(self)

        self.buttons_bar = ButtonsBar(self.master_widget)
        self.master_layout.addWidget(self.buttons_bar)
        self.buttons_bar.move_to_previous_chapter_btn.clicked.connect(self.goPreviousChapter)
        self.buttons_bar.move_to_next_chapter_btn.clicked.connect(self.goNextChapter)
        self.buttons_bar.metadata_btn.clicked.connect(self.switchToMetadataOverlay)
        self.buttons_bar.navigate_btn.clicked.connect(self.switchToBookNavigationPage)
        self.buttons_bar.toggle_readonly_btn.clicked.connect(lambda: self.editor.toggleReadOnly(self.buttons_bar.toggle_readonly_btn))
        self.buttons_bar.toggle_context_help_btn.clicked.connect(lambda: self.editor.toggleContextHelp(self.buttons_bar.toggle_context_help_btn))
        self.buttons_bar.toggle_tabletmode_btn.clicked.connect(lambda: self.editor.toggleTabletMode(self.buttons_bar.toggle_tabletmode_btn))

        self.editor = BookEditor(self.master_widget)
        self.master_layout.addWidget(self.editor)
        self.editor.presence_detection_singnal.connect(self.bookmaster.presenceDetected)
        self.buttons_bar.reload_btn.clicked.connect(self.editor.reloadCurrentText)

        self.status_bar = StatusBar(self)
        self.master_layout.addWidget(self.status_bar)


    def activate(self, book:str) -> None:
        ''' activate the editor by loading a book. `book` is the path to the .rmb file.'''
        self.bookmaster.open(book)
        self.loadTextToEditor()


################################## CHAPTER PREV/NEXT ##############################################
    def goPreviousChapter(self):
        self.bookmaster.setPrevious()
        self.loadTextToEditor()

    def goNextChapter(self):
        self.bookmaster.setNext()
        self.loadTextToEditor()

    def checkScrollPosition(self) -> None:
        ''' checks to see if the prev/next chapter buttons can lead to a valid split. '''
        if self.bookmaster is not None:     # the bookmaster is created on initial load, so this bypasses 
                                            # the check during the editorer widget's placement

            scrollbar = self.editor.verticalScrollBar()
            value = scrollbar.value()    # get the value of the scrollbar

            self.buttons_bar.move_to_previous_chapter_btn.hide()
            self.buttons_bar.move_to_next_chapter_btn.hide()

            if (value == scrollbar.minimum()) or (self.always_show_chapter_buttons):    # the displayed text is scrolled to the top or the buttons are forced
                if self.bookmaster.isPrevious():
                    self.buttons_bar.move_to_previous_chapter_btn.show()

            if (value == scrollbar.maximum()) or (self.always_show_chapter_buttons):    # the displayed text is scrolled to the bottom or the buttons are forced.
                if self.bookmaster.isNext():                                         # if the text doesn't require scrolling, the value
                    self.buttons_bar.move_to_next_chapter_btn.show()                    # will be equal to both minimum and maximum.


################################## EDITOR #########################################################
    def loadTextToEditor(self):
        ''' loads the text to the editor. '''
        split = self.bookmaster.getCurrent()
        body, cursor = self.bookmaster.getBody()
        metadata = self.bookmaster.getMetadata()
        self.editor.setTextContents(body, cursor)
        self.bookmaster.activateSplitTimer()
        self.status_bar.showLeftMessage(f'chapter {metadata["number"]}: {metadata["title"]} - {split}', timer=None, override=True)
        self.checkScrollPosition()    # force a check on the prev/next buttons
        self.editor.setFocus()


################################## METADATA #######################################################
    def switchToMetadataOverlay(self) -> None:
        metadata = self.bookmaster.getMetadata()

        metadata_editor = MetadataEditor(self)
        metadata_editor.loadMetadata(metadata)
        metadata_editor.save.connect(self.exitMetadataOverlay)
        metadata_editor.show()
        metadata_editor.setFocus()


    def exitMetadataOverlay(self, meatdata_obj:MetadataEditor, metadata:dict) -> None:
        meatdata_obj.closeOverlay()
        self.bookmaster.setMetadata(metadata)
        split = self.bookmaster.getCurrent()
        self.status_bar.showLeftMessage(f'chapter {metadata["number"]}: {metadata["title"]} - {split}', timer=None, override=True)

################################## CHAPTER NAVIGATION #############################################
    # def switchToBookNavigationPage(self) -> None:
    #     book_navigation = BookNavigation(self.bookmaster)    # initiate book navigation
    #     book_navigation.exit_navigation_signal.connect(self.exitBookNavigationPage)
    #     self.addWidget(book_navigation)
    #     self.setCurrentWidget(book_navigation)    # bring the book navigation page to the top


    # def exitBookNavigationPage(self, navigation_obj:QWidget, selected_split:str|None) -> None:
    #     navigation_obj.close()
    #     navigation_obj.deleteLater()

    #     if selected_split is not None:
    #         self.bookmaster.setSplit(selected_split)
    #         self.loadTextToEditor()

    #     self.checkScrollPosition()    # force a check on the prev/next buttons
    #     self.setCurrentWidget(self.master_widget)

    # def switchToBookNavigationPage(self) -> None:
    #     listed, unlisted = self.bookmaster.getAll()

    #     listed_data = []
    #     for item in listed:
    #         listed_data.append([item, item])
    #     unlisted_data = []
    #     for item in unlisted:
    #         unlisted_data.append([item, item])

    #     book_navigation = ChapterNavigation()
    #     book_navigation.loadChapters(listed_data, unlisted_data)
    #     book_navigation.on_exit.connect(self.exitBookNavigationPage)
    #     self.addWidget(book_navigation)

    #     self.setCurrentWidget(book_navigation)    # bring the book navigation page to the top


    # def exitBookNavigationPage(self, navigation_obj:QWidget, inorder_filenames:list, outorder_filenames:list, deleted_filenames:list, opened_filename:str|None=None) -> None:
    #     navigation_obj.close()
    #     navigation_obj.deleteLater()

    #     self.bookmaster.setInorder(inorder_filenames)
    #     self.bookmaster.setOutorder(outorder_filenames)
    #     self.bookmaster.setDeleted(deleted_filenames)

    #     if opened_filename is None:
    #         current = self.bookmaster.getCurrent()
    #         if self.bookmaster.isInorder(current):
    #             print('all ok')
    #         else:
    #             print('old split has been deleted, redirecting...')
    #             new = self.bookmaster.getAtIndex(0)
    #             self.bookmaster.setSplit(new)
    #             self.loadTextToEditor()
    #     else:
    #         print('opening new split...')
    #         self.bookmaster.setSplit(opened_filename)
    #         self.loadTextToEditor()

    #     self.checkScrollPosition()    # force a check on the prev/next buttons
    #     self.setCurrentWidget(self.master_widget)


    def switchToBookNavigationPage(self) -> None:
        splits = self.bookmaster.getSplits()
        current = self.bookmaster.getCurrent()

        book_navigation = BookNavigation(self)
        book_navigation.loadChapters(splits, current)
        book_navigation.exit.connect(self.exitBookNavigationPage)
        book_navigation.show()
        book_navigation.setFocus()

    def exitBookNavigationPage(self, navigation_obj:QWidget, selected) -> None:
        navigation_obj.close()
        navigation_obj.deleteLater()

        if selected is None:
            print('same old split.')
            return
        else:
            print('opening new split...')
            self.bookmaster.setSplit(selected)
            self.loadTextToEditor()


################################## CLOSE ##########################################################
    def atExit(self):
        self.bookmaster.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.atExit()
        self.editor.close()
        atexit.unregister(self.atExit)

        super().closeEvent(event)