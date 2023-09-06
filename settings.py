from typing import Optional
from PySide6.QtCore import *
import PySide6.QtCore
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import PySide6.QtWidgets
import sys


class Settings(QWidget):
    exit_pipeline = Signal(object, str, object)

    def __init__(self, parent: QWidget | None = None, settings:dict={}) -> None:
        super().__init__(parent)
        self.settings = {
            'cover_constraint': [150, 120],
        }
        self.settings.update(settings)
        print(self.settings)


        self.main_layout = QVBoxLayout(self)    # create the base layout


        self.navigation_widget = QWidget(self)
        self.navigation_layout = QHBoxLayout(self.navigation_widget)
        self.navigation_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.navigation_widget)

        self.save_exit_btn = QPushButton(self.navigation_widget)
        self.save_exit_btn.setText('save && exit')
        self.save_exit_btn.clicked.connect(self.triggerSaveExit)
        self.navigation_layout.addWidget(self.save_exit_btn)

        exit_btn = QPushButton(self.navigation_widget)
        exit_btn.setText('exit')
        exit_btn.clicked.connect(self.triggerExit)
        self.navigation_layout.addWidget(exit_btn)


        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)
        self.scroll_content = QWidget()
        self.scroll_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.coverSizeSettings()


################################## COVERS #########################################################
    def coverSizeSettings(self):
        self.cover_size_widget = QWidget(self.scroll_content)
        self.cover_size_layout = QGridLayout(self.cover_size_widget)
        self.cover_size_layout.setSpacing(20)
        self.scroll_content_layout.addWidget(self.cover_size_widget)

        self.cover_x_title_label = QLabel(self.cover_size_widget)
        self.cover_x_title_label.setText('Cover X max size:')
        self.cover_size_layout.addWidget(self.cover_x_title_label, 1, 1, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignCenter)

        self.cover_x_size_entry = QLineEdit(self.cover_size_widget)
        self.cover_x_size_entry.setFixedWidth(50)
        self.cover_x_size_entry.setText(str(self.settings['cover_constraint'][0]))
        self.cover_x_size_entry.textEdited.connect(self.coverXEntryChanged)
        self.cover_size_layout.addWidget(self.cover_x_size_entry, 1, 2)

        self.cover_x_slider = QSlider(Qt.Orientation.Horizontal, self.cover_size_widget)
        self.cover_x_slider.setRange(100, 1000)
        self.cover_x_slider.setValue(int(self.settings['cover_constraint'][0]))
        self.cover_x_slider.setTracking(True)
        self.cover_x_slider.valueChanged.connect(self.coverXValueChanged)
        self.cover_size_layout.addWidget(self.cover_x_slider, 1, 3)


        self.cover_y_title_label = QLabel(self.cover_size_widget)
        self.cover_y_title_label.setText('Cover Y max size:')
        self.cover_size_layout.addWidget(self.cover_y_title_label, 2, 1, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignCenter)

        self.cover_y_size_entry = QLineEdit(self.cover_size_widget)
        self.cover_y_size_entry.setFixedWidth(50)
        self.cover_y_size_entry.setText(str(self.settings['cover_constraint'][1]))
        self.cover_y_size_entry.textEdited.connect(self.coverYEntryChanged)
        self.cover_size_layout.addWidget(self.cover_y_size_entry, 2, 2)

        self.cover_y_slider = QSlider(Qt.Orientation.Horizontal, self.cover_size_widget)
        self.cover_y_slider.setRange(100, 1000)
        self.cover_y_slider.setValue(int(self.settings['cover_constraint'][1]))
        self.cover_y_slider.setTracking(True)
        self.cover_y_slider.valueChanged.connect(self.coverYValueChanged)
        self.cover_size_layout.addWidget(self.cover_y_slider, 2, 3)

    def coverXEntryChanged(self, value:str):
        if value == '':
            return
        value = int(value)
        self.cover_x_slider.setValue(value)

    def coverYEntryChanged(self, value:str):
        if value == '':
            return
        value = int(value)
        self.cover_y_slider.setValue(value)

    def coverXValueChanged(self, value):
        self.cover_x_size_entry.clear()
        self.cover_x_size_entry.setText(str(value))
        self.settings['cover_constraint'][0] = value

    def coverYValueChanged(self, value):
        self.cover_y_size_entry.clear()
        self.cover_y_size_entry.setText(str(value))
        self.settings['cover_constraint'][1] = value









    def triggerSaveExit(self):
        self.exit_pipeline.emit(self, 'save', self.settings)


    def triggerExit(self):
        self.exit_pipeline.emit(self, 'exit', None)









if __name__ == '__main__':
    app = QApplication(sys.argv)
    instance = Settings()
    instance.exit_pipeline.connect(print)
    instance.show()
    sys.exit(app.exec())