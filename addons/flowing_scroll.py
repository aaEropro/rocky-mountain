from PySide6.QtWidgets import *
from PySide6.QtCore import *
import sys
from addons.flow_layout import FlowLayout




class ResizeScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super(ResizeScrollArea, self).__init__(parent)

    def resizeEvent(self, event):
        wrapper = self.findChild(QWidget)
        flow = wrapper.findChild(FlowLayout)

        if wrapper and flow:
            width = self.viewport().width()
            height = flow.heightForWidth(width)
            size = QSize(width, height)
            point = self.viewport().rect().topLeft()
            flow.setGeometry(QRect(point, size))
            self.viewport().update()

        super(ResizeScrollArea, self).resizeEvent(event)




class ScrollingFlowWidget(QWidget):
    def __init__(self, parent=None):
        super(ScrollingFlowWidget, self).__init__(parent)
        grid = QVBoxLayout(self)
        
        scroll = ResizeScrollArea()
        self._wrapper = QWidget(scroll)
        self.flowLayout = FlowLayout(self._wrapper)
        self._wrapper.setLayout(self.flowLayout)
        scroll.setWidget(self._wrapper)
        scroll.setWidgetResizable(True)
        grid.addWidget(scroll)


    def addWidget(self, widget):
        self.flowLayout.addWidget(widget)
        widget.setParent(self._wrapper)




if __name__ == '__main__':
    app = QApplication([])
    mainWin = ScrollingFlowWidget()
    
    for i in range(20):
        btn = QPushButton(f"Button {i}")
        mainWin.addWidget(btn)

    mainWin.show()
    app.exec()
