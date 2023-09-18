import sys
from typing import Optional
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal


################################## ITEMS ##########################################################
class BaseItem(QWidget):
    open_item_in_editor = Signal(str)
    removeSignal = Signal(object)

    def __init__(self, name):
        super().__init__()
        self.master_layout = QHBoxLayout(self)

        self.label = QLabel(name)
        self.master_layout.addWidget(self.label)

    def getText(self):
        return self.label.text()

    def openInEditor(self):
        self.open_item_in_editor.emit(self.label.text())

    def deleteItem(self):
        self.removeSignal.emit(self)


class ItemInList(BaseItem):

    def __init__(self, name):
        super().__init__(name)

        self.button = QPushButton("Remove from list")
        self.button.clicked.connect(self.deleteItem)
        self.layout().addWidget(self.button)

        self.button2 = QPushButton("show")
        self.button2.clicked.connect(self.openInEditor)
        self.layout().addWidget(self.button2)


class ItemOutList(BaseItem):
    restoreSignal = Signal(object)

    def __init__(self, name):
        super().__init__(name)
        self.restore_button = QPushButton("Restore in list")
        self.restore_button.clicked.connect(self.restoreItem)
        self.layout().addWidget(self.restore_button)

        self.delete_button = QPushButton("Delete forever")
        self.delete_button.clicked.connect(self.deleteItem)
        self.layout().addWidget(self.delete_button)

        self.open_in_editor = QPushButton("show")
        self.open_in_editor.clicked.connect(self.openInEditor)
        self.layout().addWidget(self.open_in_editor)

    def restoreItem(self):
        self.restoreSignal.emit(self)

################################## LISTS ##########################################################
class BaseList(QListWidget):
    open_item_in_editor = Signal(str)

    def __init__(self):
        super().__init__()
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)

    def addItemWidgets(self, names:list):
        ''' add a series of objects. `names` is a list containing the text displayed for each item. '''
        for item in names:
            self.addItemWidget(item)

    def addItemWidget(self, name):
        ''' placeholder function. needs to be overidden. '''
        pass

    def scrapItem(self, obj:ItemInList):
        ''' removes the item `obj` from the list. '''
        for index in range(self.count()):
            if self.itemWidget(self.item(index)) == obj:
                self.takeItem(index)
                break


class InOrder(BaseList):
    moveToOutOrderSignal = Signal(str)

    def __init__(self):
        super().__init__()

    def addItemWidget(self, name):
        ''' add one object. `name` is the text displayed. '''
        item = QListWidgetItem(self)
        custom_widget = ItemInList(name)
        custom_widget.removeSignal.connect(self.scrapItem)
        custom_widget.open_item_in_editor.connect(self.open_item_in_editor.emit)
        item.setSizeHint(custom_widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, custom_widget)

    def removeItem(self, obj:ItemInList):
        ''' sends the item text trough `moveToOutOrderSignal` and removes the item from list. '''
        item_text = obj.getText()
        self.scrapItem(obj)
        self.moveToOutOrderSignal.emit(item_text)


class OutOrder(BaseList):
    restore_item = Signal(str)

    def __init__(self):
        super().__init__()

    def addItemWidget(self, name):
        print('got here')
        item = QListWidgetItem(self)
        custom_widget = ItemOutList(name)
        custom_widget.restoreSignal.connect(self.restoreItem)
        custom_widget.removeSignal.connect(self.scrapItem)
        custom_widget.open_item_in_editor.connect(self.open_item_in_editor.emit)
        item.setSizeHint(custom_widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, custom_widget)

    def restoreItem(self, obj:ItemOutList):
        item_text = obj.getText()
        self.scrapItem(obj)
        self.restore_item.emit(item_text)

################################## MAIN ###########################################################
class ChapterNavigation(QWidget):

    def __init__(self, parent:QWidget|None=None) -> None:
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)

        self.inorder_widget = InOrder()
        self.inorder_widget.addItemWidgets(['Item 1', 'Item 2', 'Item 3', 'Item 4'])
        self.inorder_widget.open_item_in_editor.connect(self.openInEditor)
        self.main_layout.addWidget(self.inorder_widget)

        self.outorder_widget = OutOrder()
        self.outorder_widget.open_item_in_editor.connect(self.openInEditor)
        self.inorder_widget.moveToOutOrderSignal.connect(self.outorder_widget.addItemWidget)
        self.outorder_widget.restore_item.connect(self.inorder_widget.addItemWidget)
        self.main_layout.addWidget(self.outorder_widget)

    def openInEditor(self, text):
        print(f'Opened in editor {text}')



app = QApplication(sys.argv)
instamce = ChapterNavigation()
instamce.show()
app.exec()
