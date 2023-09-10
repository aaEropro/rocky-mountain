from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from functools import partial

class ResponsiveContextMenu():
    def __init__(self, editor:object) -> None:
        self.editor:QTextEdit = editor

    def customContextMenu(self, event:QEvent, word_unwrapped, position_when_clicked) -> None:
        self.event = event
        self.word_unwrapped = word_unwrapped
        self.position_when_clicked = position_when_clicked

        self.context_menu = QMenu(self.editor)
        self.context_menu.setStyleSheet("""
            QMenu {
                background-color: rgb(27, 27, 27);
                border: 1px solid rgb(42, 41, 41);
            }
            QMenu::item {
                padding: 5px 20px;
                border: 1px solid transparent;
            }
            QMenu::item:enabled {
                font-weight: bold;
            }
            QMenu::item:disabled {
                color: gray;
            }
            QMenu::item:selected {
                background: rgba(0, 0, 255, 0.1);
                outline: 1px solid rgba(0, 0, 255, 0.5);
            }
        """)
        self.tagMenu()
        self.transMenu()
        self.others()

        self.context_menu.exec_(self.event.globalPos())
        self.editor.setFocus()



    def tagMenu(self):
        self.tag_menu = QMenu('tags', self.context_menu)
        self.context_menu.addMenu(self.tag_menu)

        self.add_tag_menu = QMenu('add', self.tag_menu)
        self.tag_menu.addMenu(self.add_tag_menu)

        self.add_left_tag = self.add_tag_menu.addAction('-- any   ')
        self.add_left_tag.triggered.connect(lambda: self.addTag(-1))
        
        self.add_double_tag = self.add_tag_menu.addAction('-- any --')
        self.add_double_tag.triggered.connect(lambda: self.addTag(0))

        self.add_right_tag = self.add_tag_menu.addAction('    any --')
        self.add_right_tag.triggered.connect(lambda: self.addTag(1))



        self.convert_tag_menu = QMenu('convert', self.tag_menu)
        self.tag_menu.addMenu(self.convert_tag_menu)

        self.convert_tag_dict = {}
        for item in ['e', 'a', 's', 'q', 't', 'f']:
            action = self.convert_tag_menu.addAction(f'-- {item} --')
            action.triggered.connect(partial(self.convertTag, item))
            self.convert_tag_dict[item] = action
        



        self.remove_tag_menu = QMenu('remove', self.tag_menu)
        self.tag_menu.addMenu(self.remove_tag_menu)

        self.remove_left_tag = self.remove_tag_menu.addAction('-- any   ')
        self.remove_left_tag.triggered.connect(lambda: self.removeTag(-1))
        
        self.remove_double_tag = self.remove_tag_menu.addAction('-- any --')
        self.remove_double_tag.triggered.connect(lambda: self.removeTag(0))

        self.remove_right_tag = self.remove_tag_menu.addAction('    any --')
        self.remove_right_tag.triggered.connect(lambda: self.removeTag(1))



    def transMenu(self):
        self.trans_menu = QMenu('trans', self.context_menu)
        self.context_menu.addMenu(self.trans_menu)

        self.add_trans_menu = QMenu('add', self.trans_menu)
        self.trans_menu.addMenu(self.add_trans_menu)

        self.add_left_trans = self.add_trans_menu.addAction('-- any   ')
        self.add_left_trans.triggered.connect(lambda: self.addTrans(-1))
        
        self.add_double_trans = self.add_trans_menu.addAction('-- any --')
        self.add_double_trans.triggered.connect(lambda: self.addTrans(0))

        self.add_right_trans = self.add_trans_menu.addAction('    any --')
        self.add_right_trans.triggered.connect(lambda: self.addTrans(1))



        self.convert_trans_menu = QMenu('convert', self.trans_menu)
        self.trans_menu.addMenu(self.convert_trans_menu)

        self.convert_trans_dict = {}
        for item in ['h', 'u', 'a']:
            action = self.convert_trans_menu.addAction(f'-- {item} --')
            action.triggered.connect(partial(self.convertTrans, item))
            self.convert_trans_dict[item] = action
        



        self.remove_trans_menu = QMenu('remove', self.trans_menu)
        self.trans_menu.addMenu(self.remove_trans_menu)

        self.remove_left_trans = self.remove_trans_menu.addAction('-- any   ')
        self.remove_left_trans.triggered.connect(lambda: self.removeTrans(-1))
        
        self.remove_double_trans = self.remove_trans_menu.addAction('-- any --')
        self.remove_double_trans.triggered.connect(lambda: self.removeTrans(0))

        self.remove_right_trans = self.remove_trans_menu.addAction('    any --')
        self.remove_right_trans.triggered.connect(lambda: self.removeTrans(1))

    
    def others(self):
        self.to_lowercase = self.context_menu.addAction('lowercase')
        self.to_lowercase.triggered.connect(self.toLower)

        self.to_uppercase = self.context_menu.addAction('uppercase')
        self.to_uppercase.triggered.connect(self.toUpper)

        self.to_name = self.context_menu.addAction('name')
        self.to_name.triggered.connect(self.toName)


    def placeText(self):
        text = ''.join(self.word_unwrapped)

        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(self.position_when_clicked)
        self.editor.setTextCursor(cursor)
        cursor.insertText(f'{text} ')
        self.editor.setFocus()


    def addTag(self, position):
        if position == -1:
            self.word_unwrapped[2] = f'<e>'
        if position == 1:
            self.word_unwrapped[4] = f'</e>'
        if position == 0:
            self.word_unwrapped[2] = f'<e>'
            self.word_unwrapped[4] = f'</e>'
        self.placeText()


    def convertTag(self, tag):
        self.word_unwrapped[2] = f'<{tag}>'
        self.word_unwrapped[4] = f'</{tag}>'
        self.placeText()


    def removeTag(self, position):
        if position == -1:
            self.word_unwrapped[2] = f''
        elif position == 1:
            self.word_unwrapped[4] = f''
        if position == 0:
            self.word_unwrapped[2] = f''
            self.word_unwrapped[4] = f''
        self.placeText()


    def addTrans(self, position):
        if position == -1:
            self.word_unwrapped[1] = f'[h|'
        if position == 1:
            self.word_unwrapped[6] = f']'
        if position == 0:
            self.word_unwrapped[1] = f'[h|'
            self.word_unwrapped[6] = f']'
        self.placeText()


    def convertTrans(self, tag):
        self.word_unwrapped[1] = f'[{tag}|'
        self.placeText()


    def removeTrans(self, position):
        if position == -1:
            self.word_unwrapped[1] = f''
        elif position == 1:
            self.word_unwrapped[6] = f''
        if position == 0:
            self.word_unwrapped[1] = f''
            self.word_unwrapped[6] = f''
        self.placeText()


    def toUpper(self):
        self.word_unwrapped[3] = self.word_unwrapped[3].upper()
        self.placeText()


    def toLower(self):
        self.word_unwrapped[3] = self.word_unwrapped[3].lower()
        self.placeText()


    def toName(self):
        self.word_unwrapped[3] = self.word_unwrapped[3].title()
        self.placeText()