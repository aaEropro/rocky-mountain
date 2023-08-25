from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from addons.QSwitchControl import SwitchControl
import sys


class SettingsWidget(QWidget):
    exit_settings_signal = Signal(object, dict)

    settings_dict = {
        'chapter_buttons_always_show': True,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Main layout
        layout = QVBoxLayout(self)

        exit_btn = QPushButton(self)
        exit_btn.setText('save && exit')
        exit_btn.clicked.connect(self.exitSettingsWidget)
        layout.addWidget(exit_btn)

        # Scroll area and its content
        self.scroll_area = QScrollArea(self)
        self.scroll_content = QWidget()
        self.scroll_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.scroll_area_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        self.widget1 = QWidget(self.scroll_content)
        self.widget1.setLayout(QHBoxLayout())
        self.scroll_area_layout.addWidget(self.widget1)
        self.chapter_buttons_label = QLabel(self.widget1)
        self.chapter_buttons_label.setText('Show prev/next chapter buttons regardless of scroll position')
        self.widget1.layout().addWidget(self.chapter_buttons_label)
        self.chapter_buttons_toggle = SwitchControl(self.widget1)
        self.chapter_buttons_toggle.setObjectName('chapter_buttons_always_show')
        self.widget1.layout().addWidget(self.chapter_buttons_toggle)

    
    def loadSettings(self, settings:dict) -> None:
        self.settings_dict.update(settings)
        for widget_name in self.settings_dict.keys():
            widget = self.findChild(QObject, widget_name)
            if widget:
                widget.setChecked(self.settings_dict[widget_name])


    def updateSettigsDict(self) -> None:
        for widget_name in self.settings_dict.keys():
            widget = self.findChild(QObject, widget_name)
            if widget:
                state = widget.isChecked()
                self.settings_dict[widget_name] = state


    def exitSettingsWidget(self):
        self.updateSettigsDict()    # force an update on the settings
        self.exit_settings_signal.emit(self, self.settings_dict)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    instance = SettingsWidget()
    instance.show()
    sys.exit(app.exec())