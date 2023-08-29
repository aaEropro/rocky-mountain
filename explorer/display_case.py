from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys
from explorer.cover import Cover
from addons.flow_layout import FlowLayout
from addons.flowing_scroll import ResizeScrollArea
from explorer.library_master import LibraryMaster
from functools import partial

class DisplayCase(QWidget):
    books_dict = None
    covers_dict = {}
    return_command = lambda *args, **kwargs: None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setLayout(QVBoxLayout(self))

        # last read book
        self.last_read_widget = QWidget(self)
        # self.last_read_widget.setStyleSheet('background:red')
        self.last_read_widget.setLayout(QVBoxLayout(self.last_read_widget))
        self.layout().addWidget(self.last_read_widget)

        self.last_read_message = QLabel(self.last_read_widget)
        self.last_read_message.setText('Last Read:')
        self.last_read_widget.layout().addWidget(self.last_read_message)

        self.lr_display = QWidget(self.last_read_widget)
        self.last_read_widget.layout().addWidget(self.lr_display)
        self.lr_display_layout = FlowLayout(self.lr_display)
        self.lr_display_layout.setCenterItems(True)
        self.lr_display.setLayout(self.lr_display_layout)

        # self.nothing_here_label1 = QLabel(self.lr_display)
        # self.nothing_here_label1.setText('Nothing here yet!')
        # self.lr_display_layout.addWidget(self.nothing_here_label1)


        #: other books in libary
        self.others_widget = QWidget(self)
        # self.others_widget.setStyleSheet('background:red')
        self.others_widget.setLayout(QVBoxLayout(self.others_widget))
        self.layout().addWidget(self.others_widget)

        self.others_message = QLabel(self.others_widget)
        self.others_message.setText('Other books:')
        self.others_widget.layout().addWidget(self.others_message)

        self.ot_display = QWidget(self.others_widget)
        self.others_widget.layout().addWidget(self.ot_display)
        self.ot_display_layout = FlowLayout(self.ot_display)
        self.ot_display_layout.setCenterItems(True)
        self.ot_display.setLayout(self.ot_display_layout)


    def setReturnCommand(self, return_command) -> None:
        ''' set the return command of the buttons '''
        self.return_command = return_command

        others = self.books_dict.get('others', [])
        for item in others:
            image_path, title, filename = item
            self.covers_dict[title].clicked.connect(partial(self.return_command, filename))


    def setBooksDict(self, books_dict:dict) -> None:
        '''
            set the books dictionaty from which are displayed covers.

            the dict needs to have two keys: 'last-read' and 'others'.
            
            the values stored inside must be lists of tuples, each tuple containing
            two items: the path to the image and the title of the book. 
        '''
        self.books_dict = books_dict
        self.renderCovers()


    def renderCovers(self) -> None:
        ''' trigger for rendering '''
        if self.books_dict is None:    # safeguard
            return
        
        last_read = self.books_dict.get('last-read', [])
        others = self.books_dict.get('others', [])
        
        for item in last_read:
            image_path, title, filename = item
            self.covers_dict[title] = Cover(self.lr_display)
            self.covers_dict[title].setImage(image_path)
            self.covers_dict[title].setTitle(title)
            self.covers_dict[title].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.covers_dict[title].setSizeConstraints(225, 225)
            self.covers_dict[title].clicked.connect(partial(self.return_command, filename))
            self.lr_display_layout.addWidget(self.covers_dict[title])

        for item in others:
            if item not in last_read:
                image_path, title, filename = item
                self.covers_dict[title] = Cover(self.ot_display)
                self.covers_dict[title].setImage(image_path)
                self.covers_dict[title].setTitle(title)
                self.covers_dict[title].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                self.covers_dict[title].setSizeConstraints(225, 225)
                self.covers_dict[title].clicked.connect(partial(self.return_command, filename))
                self.ot_display_layout.addWidget(self.covers_dict[title])



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.resize(600, 600)

    libmaster = LibraryMaster(r'library')
    last_read = libmaster.getLastReadBookAndCover()
    covers_list = libmaster.getBooksAndCoversList()
    print(last_read, covers_list)

    scroll = ResizeScrollArea(window)
    instance = DisplayCase()
    instance.setBooksDict({
        'last-read': last_read,
        'others': covers_list
    })

    scroll.setWidgetResizable(True)  # Let the scroll area resize its child
    scroll.setWidget(instance)
    window.setCentralWidget(scroll)

    window.show()
    sys.exit(app.exec())
