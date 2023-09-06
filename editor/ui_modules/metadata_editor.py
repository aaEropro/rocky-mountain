from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from addons.overlay import OverlayWidget


class MetadataEditor(OverlayWidget):
    save = Signal(object, dict)
    cancel = Signal()

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.cancel.connect(super().closeOverlay)
        self.master_layout = QVBoxLayout(self)
        self.setLayout(self.master_layout)

        self.container_widget = QWidget(self)
        self.container_widget.setStyleSheet("""
                                            QWidget {
                                                border: 1px solid white;
                                                background: rgb(42, 41, 41);
                                            }
                                            QPushButton {
                                                border: none;
                                                background-color: none;
                                            }
                                        """)
        self.container_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.master_layout.addWidget(self.container_widget, alignment=Qt.AlignCenter)
        self.container_layout = QGridLayout(self.container_widget)
        self.container_widget.setLayout(self.container_layout)

        self.number_label = QLabel(self.container_widget)
        self.number_label.setText('number:')
        self.container_layout.addWidget(self.number_label, 1, 1)

        self.number_entry = QLineEdit(self.container_widget)
        self.container_layout.addWidget(self.number_entry, 1, 2)

        self.title_label = QLabel(self.container_widget)
        self.title_label.setText('title:')
        self.container_layout.addWidget(self.title_label, 2, 1)

        self.title_entry = QLineEdit(self.container_widget)
        self.container_layout.addWidget(self.title_entry, 2, 2)

        self.cancel_button = QPushButton(self.container_widget)
        self.cancel_button.setText('cancel')
        self.cancel_button.clicked.connect(self.cancel.emit)
        self.container_layout.addWidget(self.cancel_button, 3, 1)

        self.save_button = QPushButton(self.container_widget)
        self.save_button.setText('save')
        self.save_button.clicked.connect(self.saveMetadata)
        self.container_layout.addWidget(self.save_button, 3, 2)


    def loadMetadata(self, metadata:dict):
        self.number_entry.setText(metadata['number'])
        self.title_entry.setText(metadata['title'])

    def saveMetadata(self):
        metadata = {
            'number': self.number_entry.text(),
            'title': self.title_entry.text()
        }
        self.save.emit(self, metadata)