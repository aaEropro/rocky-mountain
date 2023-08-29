from PySide6.QtWidgets import *
from PySide6.QtCore import *
import sys

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        if parent:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.itemList = []
        self.center_items = True  # By default, items are not centered

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def setCenterItems(self, center_items=True):
        self.center_items = center_items

    def doLayout(self, rect, testOnly):
        left, top, right, bottom = self.getContentsMargins()
        effectiveRect = rect.adjusted(left, top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0
        lineItems = []

        for item in self.itemList:
            widget = item.widget()
            spaceX = self.spacing() + widget.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                if self.center_items and lineItems:
                    excessSpace = effectiveRect.right() - (nextX - spaceX - item.sizeHint().width())
                    offsetX = excessSpace / 2
                    for lineItem in lineItems:
                        if not testOnly:
                            lineItem.setGeometry(QRect(QPoint(lineItem.geometry().x() + offsetX, lineItem.geometry().y()), lineItem.sizeHint()))
                    lineItems = []

                x = effectiveRect.x()
                y = y + lineHeight + spaceX
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            lineItems.append(item)
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        if self.center_items and lineItems:
            excessSpace = effectiveRect.right() - (x - self.spacing())
            offsetX = excessSpace / 2
            for lineItem in lineItems:
                if not testOnly:
                    lineItem.setGeometry(QRect(QPoint(lineItem.geometry().x() + offsetX, lineItem.geometry().y()), lineItem.sizeHint()))

        return y + lineHeight - rect.y() + bottom





if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    layout = FlowLayout(window)

    layout.addWidget(QLabel("Label 1"))
    layout.addWidget(QLabel("Label 1"))
    layout.addWidget(QLabel("Label 1"))
    layout.addWidget(QLabel("Label 1"))
    layout.addWidget(QLabel("Label 1"))
    layout.addWidget(QLabel("Label 1"))
    layout.addWidget(QLabel("Label 1"))
    layout.addWidget(QLabel("Label 1"))
    layout.addWidget(QLabel("Label 1"))

    # ... Add more widgets as needed

    window.setLayout(layout)
    window.show()
    sys.exit(app.exec())