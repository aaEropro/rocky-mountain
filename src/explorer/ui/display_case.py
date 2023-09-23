from PySide6.QtWidgets import QWidget, QSizePolicy, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Signal
from PySide6.QtGui import Qt
from functools import partial

from src.explorer.ui.cover import Cover
from addons.flow_layout import FlowLayout
from src.settings.data.settings_master import SettingsMasterStn


from addons.overlay import OverlayWidget



class DisplayCase(QWidget):
    books = None
    covers_dict = {}
    return_command = lambda *args, **kwargs: None

    left_click = Signal(str)
    right_click = Signal(str)
    select_library_path = Signal()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cover_size_constraints = (0, 0)
        self.overlay = QWidget()

        self.flow_layout = FlowLayout(self)    # create flow layout
        self.flow_layout.setContentsMargins(20, 20, 20, 20)
        self.flow_layout.setSpacing(20)
        self.flow_layout.setCenterItems(True)    # center items horizontaly
        self.setLayout(self.flow_layout)    # set flow layout

        SettingsMasterStn().subscribe('cover-height', self.coverHeightChanged)
        self.createLibraryButton()


    def createLibraryButton(self):
        stylesheet = '''
            QPushButton
            {
                background-color: rgb(114, 103, 189);
                color: rgb(209, 209, 209);
                font-family: Consolas;
                font-size: 13px;
                border: none;
                padding: 10;
            }
            QPushButton::hover
            {
                background-color: rgb(123, 111, 202);
            }
            QLabel
            {
                background-color: transparent;
                color: rgb(209, 209, 209);
                font-family: Consolas;
                font-weight: bold;
                font-size: 18px;
            }
        '''

        self.overlay = OverlayWidget(self)
        overlay_layout = QVBoxLayout(self.overlay)

        widget = QWidget(self.overlay)
        widget.setStyleSheet(stylesheet)
        widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        overlay_layout.addWidget(widget)
        layout = QVBoxLayout(widget)
        layout.setSpacing(30)

        message = QLabel()
        message.setText('you have not selected a library')
        layout.addWidget(message, alignment=Qt.AlignmentFlag.AlignHCenter)

        library_path_button = QPushButton()
        library_path_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        library_path_button.setText('Select Library')
        library_path_button.clicked.connect(self.select_library_path.emit)
        layout.addWidget(library_path_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.overlay.show()


    def setBooks(self, books:list, size_constraints:tuple=(250,250)) -> None:
        '''
            set the books list from which are displayed covers.

            the list has to contain tuples, each tuple having three items: 
            the path to the image, the title of the book, and the name of the book file from the library.

            ex: ('library\hilldiggers.png', 'Neal Asher: Hilldiggers', 'hildiggers.rmb') 
        '''
        self.overlay.close()

        self.books = books
        self.cover_size_constraints = size_constraints
        self.renderCovers()


    def renderCovers(self) -> None:
        ''' trigger for rendering. '''
        if self.books is None:    # safeguard
            return
        
        for item in self.books:
            image_path, title, filename = item

            cover = Cover(self)
            cover.setImage(image_path)
            cover.setTitle(title)
            cover.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding)
            cover.setSizeConstraints(self.cover_size_constraints[0], self.cover_size_constraints[1])
            cover.left_click.connect(partial(self.left_click.emit, filename))
            cover.right_click.connect(partial(self.right_click.emit, filename))

            self.covers_dict[title] = cover
            self.flow_layout.addWidget(self.covers_dict[title])


    def setCoverSizeConstraints(self, constraints:list) -> None:
        if constraints == self.cover_size_constraints:
            return
        self.cover_size_constraints = constraints
        for item in self.covers_dict.keys():
            self.covers_dict[item].setSizeConstraints(constraints[0], constraints[1])


    def setCoverHeightConstraints(self, height:int) -> None:
        ''' update the height constraint of all covers in the library. '''
        for cover in self.covers_dict.keys():
            self.covers_dict[cover].setHeightConstraint(height)
        print(f'changed constraint {height}')


    def coverHeightChanged(self):
        height = SettingsMasterStn().getSpecific('cover-height')
        self.setCoverHeightConstraints(height)