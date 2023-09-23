import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal



################################## ITEMS ##########################################################
class BaseItem(QWidget):
    open_item_in_editor = Signal(str)
    removeSignal = Signal(object)

    def __init__(self, data:list) -> None:
        super().__init__()
        self.master_layout = QHBoxLayout(self)

        self.text = data[0]
        self.name = data[1]

        self.label = QLabel(f'{self.text} -- {self.name}')
        self.master_layout.addWidget(self.label)

    def getText(self) -> str:
        return self.text
    
    def getFileName(self) -> str:
        return self.name
    
    def getData(self) -> list[str]:
        return [self.text, self.name]

    def openInEditor(self) -> None:
        self.open_item_in_editor.emit(self.getFileName())

    def deleteItem(self) -> None:
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

    def addItemWidgets(self, names:list) -> None:
        ''' add a series of objects. `names` is a list containing the text displayed for each item. '''
        for item in names:
            self.addItemWidget(item)

    def addItemWidget(self, name) -> None:
        ''' placeholder function. needs to be overidden. '''
        pass

    def scrapItem(self, obj:ItemInList) -> None:
        ''' removes the item `obj` from the list. '''
        for index in range(self.count()):
            if self.itemWidget(self.item(index)) == obj:
                self.takeItem(index)
                break

    def getItemsData(self) -> list[list[str]]:
        ''' returns a list containing the data ([text, filename]) of items in the order they are shown. '''
        items_data = []
        for index in range(self.count()):
            widget:BaseItem = self.itemWidget(self.item(index))
            if widget:
                items_data.append(widget.getData())
        return items_data
    
    def getItemsFilenames(self) -> list[str]:
        ''' returns a list containing the filenames of items in the order they are shown. '''
        items_filenames = []
        for index in range(self.count()):
            widget:BaseItem = self.itemWidget(self.item(index))
            if widget:
                items_filenames.append(widget.getFileName())
        return items_filenames

class InOrder(BaseList):
    moveToOutOrderSignal = Signal(list)  # Signal to send list data

    def __init__(self):
        super().__init__()

    def addItemWidget(self, data: list):  # Now accepting a list data
        item = QListWidgetItem(self)
        custom_widget = ItemInList(data)  # Sending list data to the widget
        custom_widget.removeSignal.connect(self.removeItem)
        custom_widget.open_item_in_editor.connect(self.open_item_in_editor.emit)
        item.setSizeHint(custom_widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, custom_widget)

    def removeItem(self, obj: ItemInList):
        data = obj.getData()  # Fetch the list data
        self.scrapItem(obj)
        self.moveToOutOrderSignal.emit(data)  # Emitting list data

class OutOrder(BaseList):
    restore_item = Signal(list)  # Signal to send list data

    def __init__(self):
        super().__init__()

    def addItemWidget(self, data: list):  # Now accepting a list data
        item = QListWidgetItem(self)
        custom_widget = ItemOutList(data)  # Sending list data to the widget
        custom_widget.restoreSignal.connect(self.restoreItem)
        custom_widget.removeSignal.connect(self.scrapItem)
        custom_widget.open_item_in_editor.connect(self.open_item_in_editor.emit)
        item.setSizeHint(custom_widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, custom_widget)

    def restoreItem(self, obj: ItemOutList):
        data = obj.getData()  # Fetch the list data
        self.scrapItem(obj)
        self.restore_item.emit(data)  # Emitting list data

################################## MAIN ###########################################################
class ChapterNavigation(QWidget):
    on_exit = Signal(object, list, list, list, object)

    def instanciate(self) -> None:
        self.all_items_filenames = []
        self.opened = None

    def __init__(self, parent:QWidget|None=None) -> None:
        self.instanciate()

        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)

        self.exit_btn = QPushButton(self)
        self.exit_btn.setText('exit')
        self.exit_btn.clicked.connect(self.exitNavigation)
        self.main_layout.addWidget(self.exit_btn)

        self.inorder_widget = InOrder()
        self.inorder_widget.open_item_in_editor.connect(self.openInEditor)
        self.main_layout.addWidget(self.inorder_widget)

        self.outorder_widget = OutOrder()
        self.outorder_widget.open_item_in_editor.connect(self.openInEditor)
        self.inorder_widget.moveToOutOrderSignal.connect(self.outorder_widget.addItemWidget)
        self.outorder_widget.restore_item.connect(self.inorder_widget.addItemWidget)
        self.main_layout.addWidget(self.outorder_widget)

    def loadChapters(self, listed:list, unlisted:list):
        for item in listed+unlisted:
            self.all_items_filenames.append(item[1])

        self.inorder_widget.addItemWidgets(listed)
        self.outorder_widget.addItemWidgets(unlisted)

    def openInEditor(self, filename):
        print(f'Opened in editor {filename}')
        self.opened = filename
        self.exitNavigation()

    def exitNavigation(self):
        inorder_items = self.inorder_widget.getItemsFilenames()
        outorder_items = self.outorder_widget.getItemsFilenames()
        deleted_items = []
        for item in self.all_items_filenames:
            if (not item in inorder_items) and (not item in outorder_items):
                deleted_items.append(item)

        self.on_exit.emit(self, inorder_items, outorder_items, deleted_items, self.opened)
                


if __name__ == '__main__':
    def ex(obj, inorder, outorder, deleted):
        print('in order:', inorder)
        print('out order:', outorder)
        print('deleted:', deleted)
        sys.exit()

    app = QApplication(sys.argv)
    instamce = ChapterNavigation()
    instamce.loadChapters([['prologue', 'split_001.gmd'], ['chapter 1', 'split_002.gmd'], ['chapter 2', 'split_003.gmd'], ['chapter 3', 'split_004.gmd'], ['epilogue', 'split_005.gmd']], [])
    instamce.on_exit.connect(ex)
    instamce.show()
    app.exec()