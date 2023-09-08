from typing import Optional
from PySide6.QtCore import *
import PySide6.QtCore
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import PySide6.QtWidgets
import sys
from src.settings.data.settings_master import SettingsMasterStn


class Settings(QWidget):
    exit_pipeline = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.settings = SettingsMasterStn().getData()

        self.main_layout = QVBoxLayout(self)    # create the base layout

        self.navigation_widget = QWidget(self)
        self.navigation_layout = QHBoxLayout(self.navigation_widget)
        self.navigation_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.navigation_widget)

        self.save_exit_btn = QPushButton(self.navigation_widget)
        self.save_exit_btn.setText('save && exit')
        self.save_exit_btn.clicked.connect(self.triggerSaveExit)
        self.navigation_layout.addWidget(self.save_exit_btn)

        self.exit_btn = QPushButton(self.navigation_widget)
        self.exit_btn.setText('exit')
        self.exit_btn.clicked.connect(self.triggerCancelExit)
        self.navigation_layout.addWidget(self.exit_btn)

        self.warning_on = False
        self.caution_label = QLabel(self)
        self.caution_label.setText('Caution! The changed settings have to be saved!')
        self.caution_label.setWordWrap(True)
        self.caution_label.setStyleSheet('border: 2px solid red; color: red')
        self.main_layout.addWidget(self.caution_label)
        self.caution_label.hide()


        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)
        self.scroll_content = QWidget()
        self.scroll_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.coverSizeSettings()
        self.libraryPathSettings()


################################## COVERS #########################################################
    def coverSizeSettings(self):
        self.cover_size_widget = QWidget(self.scroll_content)
        self.cover_size_layout = QGridLayout(self.cover_size_widget)
        self.cover_size_layout.setSpacing(20)
        self.scroll_content_layout.addWidget(self.cover_size_widget)


        self.cover_y_title_label = QLabel(self.cover_size_widget)
        self.cover_y_title_label.setText('Cover Y max size:')
        self.cover_size_layout.addWidget(self.cover_y_title_label, 2, 1, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignCenter)

        self.cover_y_size_entry = QLineEdit(self.cover_size_widget)
        self.cover_y_size_entry.setFixedWidth(50)
        self.cover_y_size_entry.setText(str(self.settings['cover-height']))
        self.cover_y_size_entry.textEdited.connect(self.coverYEntryChanged)
        self.cover_size_layout.addWidget(self.cover_y_size_entry, 2, 2)

        self.cover_y_slider = QSlider(Qt.Orientation.Horizontal, self.cover_size_widget)
        self.cover_y_slider.setRange(100, 1000)
        self.cover_y_slider.setValue(int(self.settings['cover-height']))
        self.cover_y_slider.setTracking(True)
        self.cover_y_slider.valueChanged.connect(self.coverYValueChanged)
        self.cover_size_layout.addWidget(self.cover_y_slider, 2, 3)

    def coverYEntryChanged(self, value:str):
        if value == '':
            return
        value = int(value)
        self.cover_y_slider.setValue(value)

    def coverYValueChanged(self, value):
        self.cover_y_size_entry.clear()
        self.cover_y_size_entry.setText(str(value))
        self.settings['cover-height'] = value
        self.triggerSettingChange()

################################## LIBRARY PATH ###################################################
    def libraryPathSettings(self):
        self.library_path_widget = QWidget(self.scroll_content)
        self.library_path_layout = QGridLayout(self.library_path_widget)
        self.scroll_content_layout.addWidget(self.library_path_widget)

        self.library_path_label = QLabel(self.library_path_widget)
        self.library_path_label.setText('Library path:')
        self.library_path_layout.addWidget(self.library_path_label, 1, 1, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignCenter)

        self.library_path_button = QPushButton(self.library_path_widget)
        self.library_path_button.setText(self.settings['library-path'])
        self.library_path_button.clicked.connect(self.changeLibraryPath)
        self.library_path_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.library_path_layout.addWidget(self.library_path_button, 1, 2)
        print('pass')


    def changeLibraryPath(self):
        folder_name = QFileDialog.getExistingDirectory(None, "Select Folder")
        if folder_name:
            self.library_path_button.setText(folder_name)
            self.settings['library-path'] = folder_name
            self.triggerSettingChange()
    #############################################################################






    def triggerSettingChange(self):
        if self.warning_on:
            return
        self.caution_label.show()
        self.warning_on = True


    def triggerSaveExit(self):
        SettingsMasterStn().updateData(self.settings)
        self.exit_pipeline.emit(self)

    def triggerCancelExit(self):
        self.exit_pipeline.emit(self)









if __name__ == '__main__':
    app = QApplication(sys.argv)
    instance = Settings()
    instance.exit_pipeline.connect(print)
    instance.show()
    sys.exit(app.exec())