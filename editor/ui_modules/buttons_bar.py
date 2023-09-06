from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class ButtonsBar(QWidget):
    def __init__(self, master:object) -> None:
        super().__init__(master)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        #::: previous chapter
        self.move_to_previous_chapter_widget = QWidget(self)
        self.move_to_previous_chapter_widget.setLayout(QVBoxLayout())
        self.move_to_previous_chapter_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.move_to_previous_chapter_widget)
        self.move_to_previous_chapter_btn = QPushButton(self.move_to_previous_chapter_widget)   # previous chapter button
        self.move_to_previous_chapter_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.move_to_previous_chapter_btn.setText('<- previous chapter')
        self.move_to_previous_chapter_widget.layout().addWidget(self.move_to_previous_chapter_btn)

        #::: spacer left
        self.spacer_left = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout().addItem(self.spacer_left)

        #: buttons
        # self.settings_btn = QPushButton(self)
        # self.settings_btn.setText('settings')
        # self.layout().addWidget(self.settings_btn)

        self.metadata_btn = QPushButton(self)
        self.metadata_btn.setText('metadata')
        self.layout().addWidget(self.metadata_btn)

        self.navigate_btn = QPushButton(self)
        self.navigate_btn.setText('navigate')
        self.layout().addWidget(self.navigate_btn)

        self.reload_btn = QPushButton(self)
        self.reload_btn.setText('reload')
        self.layout().addWidget(self.reload_btn)
        
        self.toggle_tabletmode_btn = QPushButton(self)
        self.toggle_tabletmode_btn.setCheckable(True)
        self.toggle_tabletmode_btn.setText('tablet')
        self.layout().addWidget(self.toggle_tabletmode_btn)

        self.toggle_readonly_btn = QPushButton(self)
        self.toggle_readonly_btn.setCheckable(True)
        self.toggle_readonly_btn.setText('read-only')
        self.layout().addWidget(self.toggle_readonly_btn)

        self.toggle_context_help_btn = QPushButton(self)
        self.toggle_context_help_btn.setCheckable(True)
        self.toggle_context_help_btn.setText('context')
        self.layout().addWidget(self.toggle_context_help_btn)

        #::: spacer right
        self.spacer_right = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout().addItem(self.spacer_right)

        #::: previous chapter
        self.move_to_next_chapter_widget = QWidget(self)
        self.move_to_next_chapter_widget.setLayout(QVBoxLayout())
        self.move_to_next_chapter_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.move_to_next_chapter_widget)
        self.move_to_next_chapter_btn = QPushButton(self.move_to_next_chapter_widget)   # next chapter button
        self.move_to_next_chapter_btn.setText('next chapter ->')
        self.move_to_next_chapter_widget.layout().addWidget(self.move_to_next_chapter_btn)
        
        nav_buttons_width = max(self.move_to_previous_chapter_btn.sizeHint().width(), self.move_to_next_chapter_btn.sizeHint().width())
        nav_buttons_height = max(self.move_to_previous_chapter_btn.sizeHint().height(), self.move_to_next_chapter_btn.sizeHint().height())
        self.move_to_previous_chapter_widget.setFixedSize(QSize(nav_buttons_width, nav_buttons_height))
        self.move_to_next_chapter_widget.setFixedSize(QSize(nav_buttons_width, nav_buttons_height))
