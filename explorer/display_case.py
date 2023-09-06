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
    books = None
    covers_dict = {}
    return_command = lambda *args, **kwargs: None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cover_size_constraints = (0, 0)

        self.flow_layout = FlowLayout(self)    # create flow layout
        self.flow_layout.setCenterItems(True)    # cebter items horisontaly
        self.setLayout(self.flow_layout)    # set flow layout


    def setReturnCommand(self, return_command) -> None:
        ''' set the return command of the buttons '''
        self.return_command = return_command

        for item in self.books:
            image_path, title, filename = item
            self.covers_dict[title].clicked.connect(partial(self.return_command, filename))


    def setBooks(self, books:list, size_constraints:tuple=(250,250)) -> None:
        '''
            set the books list from which are displayed covers.

            the list has to contain tuples, each tuple having three items: 
            the path to the image, the title of the book, and the name of the book file from the library.

            ex: ('library\hilldiggers.png', 'Neal Asher: Hilldiggers', 'hildiggers.rmb') 
        '''
        self.books = books
        self.cover_size_constraints = size_constraints
        self.renderCovers()


    def renderCovers(self) -> None:
        ''' trigger for rendering. '''
        if self.books is None:    # safeguard
            return
        
        for item in self.books:
            image_path, title, filename = item
            self.covers_dict[title] = Cover(self)
            self.covers_dict[title].setImage(image_path)
            self.covers_dict[title].setTitle(title)
            self.covers_dict[title].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.covers_dict[title].setSizeConstraints(self.cover_size_constraints[0], self.cover_size_constraints[1])
            self.covers_dict[title].clicked.connect(partial(self.return_command, filename))
            self.flow_layout.addWidget(self.covers_dict[title])


    def setCoverSizeConstraints(self, constraints:list) -> None:
        if constraints == self.cover_size_constraints:
            return
        self.cover_size_constraints = constraints
        for item in self.covers_dict.keys():
            self.covers_dict[item].setSizeConstraints(constraints[0], constraints[1])

















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
    instance.setBooks(covers_list)

    scroll.setWidgetResizable(True)  # Let the scroll area resize its child
    scroll.setWidget(instance)
    window.setCentralWidget(scroll)

    window.show()
    sys.exit(app.exec())
