import sys
import PySide6.QtGui
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import os
from addons.png_icon_manipulation import colorizeImage, resizeImage


class SquareClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.clicked.emit()
        return True

    def resizeEvent(self, event):
        print(self.width(), self.height())
        parent_policy = self.parentWidget().sizePolicy()
        
        # Check if parent allows horizontal stretching
        if parent_policy.horizontalPolicy() in [QSizePolicy.Expanding, QSizePolicy.MinimumExpanding, QSizePolicy.Preferred]:
            side = max(self.width(), self.height())
        else:
            side = min(self.width(), self.height())
        
        self.setFixedSize(side, side)


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


        bar_widget = QWidget(main_widget)
        bar_widget.setStyleSheet('''background: gray''')
        bar_layout = QHBoxLayout(bar_widget)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_widget.setLayout(bar_layout)
        main_layout.addWidget(bar_widget)

        buttons_widget = QWidget(bar_widget)
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(0)
        buttons_widget.setLayout(buttons_layout)
        bar_layout.addWidget(buttons_widget)

        settings_button = SquareClickableLabel(buttons_widget)
        settings_button.setStyleSheet('''background: red''')
        settings_icon = QPixmap(os.path.join('icons', 'icons8-settings-96.png'))
        settings_button.setPixmap(settings_icon)
        buttons_layout.addWidget(settings_button)

        # button2 = QLabel(buttons_widget)
        button2 = SquareClickableLabel(buttons_widget)
        button2.setStyleSheet('''background: green''')
        settings_icon = QPixmap(os.path.join('icons', 'icons8-settings-96.png'))
        settings_icon = settings_icon.scaled(20, 20, Qt.KeepAspectRatio)
        button2.setPixmap(settings_icon)
        buttons_layout.addWidget(button2)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
