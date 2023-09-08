from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from functools import partial
from src.editor.data.book_master import BookMaster

class BookNavigation(QWidget):
    exit_navigation_signal = Signal(object, object)

    def __init__(self, book_master:BookMaster=None):
        super().__init__()

        # Main layout
        layout = QVBoxLayout(self)

        exit_btn = QPushButton(self)
        exit_btn.setText('exit')
        exit_btn.clicked.connect(lambda: self.exit_navigation_signal.emit(self, None))
        layout.addWidget(exit_btn)

        # Scroll area and its content
        self.scroll_area = QScrollArea(self)
        self.scroll_content = QWidget()
        self.scroll_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.scroll_area_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        if book_master:
            self.bookmaster = book_master
            self.queryBookmaster()

    def queryBookmaster(self):
        split_order, split_not_present_in_order_list = self.bookmaster.getAll()

        splits_present_buttons_dict = {}
        splits_deleted_buttons_dict = {}

        for child in self.scroll_content.children():
            if isinstance(child, QWidget):    # make sure it's a widget
                child.deleteLater()    # schedule the widget for deletion

        for index, split in enumerate(split_order):
            widget = QWidget()
            widget.setContentsMargins(0, 0, 0, 0)
            hbox = QHBoxLayout(widget)
            
            btn = QPushButton(split)
            btn.clicked.connect(partial(self.loadSpecificSplit, split))
            hbox.addWidget(btn)

            delete = QPushButton("remove")
            delete.clicked.connect(partial(self.removeSpecificSplit, split))
            hbox.addWidget(delete)

            splits_present_buttons_dict[index] = widget
            self.scroll_area_layout.addWidget(widget)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.scroll_area_layout.addWidget(line)

        for index, split in enumerate(split_not_present_in_order_list):
            widget = QWidget()
            widget.setContentsMargins(0, 0, 0, 0)
            hbox = QHBoxLayout(widget)
            
            btn = QPushButton(split)
            btn.clicked.connect(partial(self.loadSpecificSplit, split))
            hbox.addWidget(btn)

            delete = QPushButton("del")
            delete.clicked.connect(partial(self.deleteSpecificSplit, split))
            hbox.addWidget(delete)

            restore = QPushButton("restore")
            restore.clicked.connect(partial(self.restoreSpecificSplit, split))
            hbox.addWidget(restore)

            splits_deleted_buttons_dict[index] = widget
            self.scroll_area_layout.addWidget(widget)
    

    def loadSpecificSplit(self, split_name:str) -> None:    # loades the split order
        self.exit_navigation_signal.emit(self, split_name)


    def removeSpecificSplit(self, split_name:str) -> None:    # removes the split from the order
        if self.bookmaster is not None:
            self.bookmaster.removeSpecificSplit(split_name)
            self.queryBookmaster()


    def restoreSpecificSplit(self, split_name:str) -> None:    # restores the split to the order
        if self.bookmaster is not None:
            self.bookmaster.restoreSpecificSplit(split_name)
            self.queryBookmaster()

    
    def deleteSpecificSplit(self, split_name:str) -> None:    # deletes the split from RMB file
        if self.bookmaster is not None:
            self.bookmaster.deleteSpecificSplit(split_name)
            self.queryBookmaster()