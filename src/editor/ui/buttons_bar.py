from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import os

from addons.png_icon_manipulation import colorizeImage

DIR = os.path.dirname(os.path.abspath(__import__('__main__').__file__))


class ButtonsBar(QWidget):
    def __init__(self, master:object) -> None:
        super().__init__(master)
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet = '''
            QWidget
            {
                background-color: rgb(32, 32, 32);
            }
            QPushButton
            {
                background-color: rgb(31, 31, 31);
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
        '''
        self.setStyleSheet(stylesheet)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.master_layout = QHBoxLayout(self)
        self.master_layout.setContentsMargins(*[0]*4)

        previous_icon = QPixmap(os.path.join(DIR, 'assets', 'icons', 'previous.png'))
        next_icon = QPixmap(os.path.join(DIR, 'assets', 'icons', 'next.png'))

        previous_icon = QPixmap(r'C:\Users\Jovanni\Documents\GitHub\rocky-mountain\assets\icons\previous.png')
        next_icon = QPixmap(r'C:\Users\Jovanni\Documents\GitHub\rocky-mountain\assets\icons\next.png')

        previous_icon = colorizeImage(previous_icon, QColor(209, 209, 209))
        next_icon = colorizeImage(next_icon, QColor(209, 209, 209))

        self.move_to_previous_chapter_btn = QPushButton()
        self.move_to_previous_chapter_btn.setIcon(previous_icon)
        self.move_to_previous_chapter_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.master_layout.addWidget(self.move_to_previous_chapter_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self.otherButtons()

        self.move_to_next_chapter_btn = QPushButton()
        self.move_to_next_chapter_btn.setIcon(next_icon)
        self.move_to_next_chapter_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.master_layout.addWidget(self.move_to_next_chapter_btn, alignment=Qt.AlignmentFlag.AlignRight)



    def otherButtons(self):
        widget_left = QWidget()
        widget_left.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.master_layout.addWidget(widget_left)
        layout_left = QHBoxLayout(widget_left)
        layout_left.setContentsMargins(10, 0, 5, 0)

        metadata_icon = QPixmap(os.path.join(DIR, 'assets', 'icons', 'tag.png'))
        metadata_icon = colorizeImage(metadata_icon, QColor(209, 209, 209))
        navigate_icon = QPixmap(os.path.join(DIR, 'assets', 'icons', 'layer.png'))
        navigate_icon = colorizeImage(navigate_icon, QColor(209, 209, 209))
        reload_icon = QPixmap(os.path.join(DIR, 'assets', 'icons', 'repeat.png'))
        reload_icon = colorizeImage(reload_icon, QColor(209, 209, 209))

        self.metadata_btn = QPushButton()
        # self.metadata_btn.setText('metadata')
        self.metadata_btn.setIcon(metadata_icon)
        layout_left.addWidget(self.metadata_btn)

        self.navigate_btn = QPushButton()
        # self.navigate_btn.setText('navigate')
        self.navigate_btn.setIcon(navigate_icon)
        layout_left.addWidget(self.navigate_btn)

        self.reload_btn = QPushButton()
        # self.reload_btn.setText('reload')
        self.reload_btn.setIcon(reload_icon)
        layout_left.addWidget(self.reload_btn)

        self.master_layout.addStretch()

        widget_right = QWidget()
        widget_right.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.master_layout.addWidget(widget_right)
        layout_right = QHBoxLayout(widget_right)
        layout_right.setContentsMargins(5, 0, 10, 0)
        
        self.toggle_tabletmode_btn = QPushButton()
        self.toggle_tabletmode_btn.setCheckable(True)
        self.toggle_tabletmode_btn.setText('tablet')
        layout_right.addWidget(self.toggle_tabletmode_btn)

        self.toggle_readonly_btn = QPushButton()
        self.toggle_readonly_btn.setCheckable(True)
        self.toggle_readonly_btn.setText('read-only')
        layout_right.addWidget(self.toggle_readonly_btn)

        self.toggle_context_help_btn = QPushButton()
        self.toggle_context_help_btn.setCheckable(True)
        self.toggle_context_help_btn.setText('context')
        layout_right.addWidget(self.toggle_context_help_btn)





if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    instance = QMainWindow()
    buttons_bar = ButtonsBar(instance)
    instance.setCentralWidget(buttons_bar)
    instance.show()
    sys.exit(app.exec())