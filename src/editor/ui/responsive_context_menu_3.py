from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import os
from functools import partial
from configobj import ConfigObj

from src.settings.data.settings_master import SettingsMasterStn

class ResponsiveContextMenu():
    def __init__(self, editor:object) -> None:
        self.editor:QTextEdit = editor

        self.validateDataFile()
        self.loadData()

    def validateDataFile(self):
        libpath = SettingsMasterStn().getSpecific('library-path')
        datapath = os.path.join(libpath, 'data')
        
        if not os.path.isdir(datapath):
            os.mkdir(datapath)

        datafile_path = os.path.join(datapath, 'menu-items-hits.ini')
        if not os.path.isfile(datafile_path):
            data = {
                'tags':
                {
                    'e': 0,
                    'a': 0,
                    's': 0,
                    'q': 0,
                    't': 0,
                    'f': 0,
                    'o': 0,
                },
                'trans':
                {
                    '0': 0, 
                    'h': 0, 
                    'u': 0,
                    'a': 0,
                }
            }
            file = ConfigObj(data)
            file.filename = datafile_path
            file.write()

    def loadData(self):
        libpath = SettingsMasterStn().getSpecific('library-path')
        datafile_path = os.path.join(libpath, 'data', 'menu-items-hits.ini')

        file = ConfigObj(datafile_path)
        self.tags_usage = file['tags']
        self.trans_usage = file['trans']

    
    def saveData(self):
        libpath = SettingsMasterStn().getSpecific('library-path')
        datafile_path = os.path.join(libpath, 'data', 'menu-items-hits.ini')

        data = {'tags': self.tags_usage, 'trans': self.trans_usage}
        file = ConfigObj(data)
        file.filename = datafile_path
        file.write()


    def customContextMenu(self, event:QEvent, word_unwrapped:list, position_when_clicked:int) -> None:
        self.event:QEvent = event
        self.word_unwrapped:list = word_unwrapped
        self.position_when_clicked:int = position_when_clicked

        self.context_menu = QMenu(self.editor)
        self.context_menu.setStyleSheet("""
            QMenu {
                background-color: rgb(27, 27, 27);
                color: rgb(209, 209, 209);
                border: 1px solid rgb(42, 41, 41);
                font-size: 20px;
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
                background: rgb(123, 111, 202);
                outline: 1px solid rgba(0, 0, 255, 0.5);
            }
        """)
        self.tagMenu()
        self.transMenu()
        self.others()

        self.context_menu.exec(self.event.globalPos())
        self.saveData()
        self.editor.setFocus()


    def tagMenu(self):
        sorted_items = sorted(self.tags_usage.items(), key=lambda item: item[1], reverse=True)
        self.tags_usage = {k: int(v) for k, v in sorted_items}

        self.tag_menu = QMenu('tags', self.context_menu)
        self.context_menu.addMenu(self.tag_menu)

        self.add_left_tag_menu = QMenu('++ any', self.tag_menu)
        self.tag_menu.addMenu(self.add_left_tag_menu)
        self.add_left_tag_dict = {}
        for item in self.tags_usage.keys():
            action = self.add_left_tag_menu.addAction(f'++ {item}   ')
            action.triggered.connect(partial(self.addTag, -1, item))
            action.triggered.connect(partial(self.incrementUsage, 'tags', item))
            self.add_left_tag_dict[item] = action

        self.add_double_tag_menu = QMenu('++ any ++', self.tag_menu)
        self.tag_menu.addMenu(self.add_double_tag_menu)
        self.add_double_tag_dict = {}
        for item in self.tags_usage.keys():
            action = self.add_double_tag_menu.addAction(f'++ {item} ++')
            action.triggered.connect(partial(self.addTag, 0, item))
            action.triggered.connect(partial(self.incrementUsage, 'tags', item))
            self.add_double_tag_dict[item] = action

        self.add_right_tag_menu = QMenu('any ++', self.tag_menu)
        self.tag_menu.addMenu(self.add_right_tag_menu)
        self.add_right_tag_dict = {}
        for item in self.tags_usage.keys():
            action = self.add_right_tag_menu.addAction(f'      {item} ++')
            action.triggered.connect(partial(self.addTag, 1, item))
            action.triggered.connect(partial(self.incrementUsage, 'tags', item))
            self.add_right_tag_dict[item] = action

        self.convert_tag_dict = {}
        for item in self.tags_usage.keys():
            action = self.tag_menu.addAction(f'   -> {item} <-')
            action.triggered.connect(partial(self.convertTag, item))
            action.triggered.connect(partial(self.incrementUsage, 'tags', item))
            self.convert_tag_dict[item] = action

        self.remove_left_tag = self.tag_menu.addAction('  -- any   ')
        self.remove_left_tag.triggered.connect(lambda: self.removeTag(-1))
        self.remove_double_tag = self.tag_menu.addAction('  -- any --')
        self.remove_double_tag.triggered.connect(lambda: self.removeTag(0))
        self.remove_right_tag = self.tag_menu.addAction('      any --')
        self.remove_right_tag.triggered.connect(lambda: self.removeTag(1))


    def transMenu(self):
        sorted_items = sorted(self.trans_usage.items(), key=lambda item: item[1], reverse=True)
        self.trans_usage = {k: int(v) for k, v in sorted_items}

        self.trans_menu = QMenu('trans', self.context_menu)
        self.context_menu.addMenu(self.trans_menu)

        self.add_left_trans_menu = QMenu('++ any   ', self.trans_menu)
        self.trans_menu.addMenu(self.add_left_trans_menu)
        self.add_left_trans_dict = {}
        for item in self.trans_usage.keys():
            action = self.add_left_trans_menu.addAction(f'-> {item}')
            action.triggered.connect(partial(self.addTrans, -1, item))
            action.triggered.connect(partial(self.incrementUsage, 'trans', item))
            self.add_left_trans_dict[item] = action

        self.add_double_trans_menu = QMenu('++ any ++', self.trans_menu)
        self.trans_menu.addMenu(self.add_double_trans_menu)
        self.add_center_trans_dict = {}
        for item in self.trans_usage.keys():
            action = self.add_double_trans_menu.addAction(f'-> {item} <-')
            action.triggered.connect(partial(self.addTrans, 0, item))
            action.triggered.connect(partial(self.incrementUsage, 'trans', item))
            self.add_center_trans_dict[item] = action

        self.add_right_trans_menu = self.trans_menu.addAction('      any ++')
        self.add_right_trans_menu.triggered.connect(lambda: self.addTrans(1, ''))

        self.convert_trans_dict = {}
        for item in self.trans_usage.keys():
            action = self.trans_menu.addAction(f'   -> {item} <-')
            action.triggered.connect(partial(self.convertTrans, item))
            action.triggered.connect(partial(self.incrementUsage, 'trans', item))
            self.convert_trans_dict[item] = action
        
        self.remove_left_trans = self.trans_menu.addAction('  -- any   ')
        self.remove_left_trans.triggered.connect(lambda: self.removeTrans(-1))
        self.remove_double_trans = self.trans_menu.addAction('  -- any --')
        self.remove_double_trans.triggered.connect(lambda: self.removeTrans(0))
        self.remove_right_trans = self.trans_menu.addAction('      any --')
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

    def incrementUsage(self, category, item):
        if category == 'tags':
            self.tags_usage[item] += 1
        elif category == 'trans':
            self.trans_usage[item] += 1


    def addTag(self, position, tag):
        if position == -1:
            self.word_unwrapped[2] = f'<{tag}>'
        if position == 1:
            self.word_unwrapped[4] = f'</{tag}>'
        if position == 0:
            self.word_unwrapped[2] = f'<{tag}>'
            self.word_unwrapped[4] = f'</{tag}>'
        self.placeText()


    def convertTag(self, tag):
        if self.word_unwrapped[2] != '':
            self.word_unwrapped[2] = f'<{tag}>'
        if self.word_unwrapped[4] != '':
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


    def addTrans(self, position, tag):
        if position == -1:
            self.word_unwrapped[1] = f'[{tag}|'
        if position == 1:
            self.word_unwrapped[6] = f']'
        if position == 0:
            self.word_unwrapped[1] = f'[{tag}|'
            self.word_unwrapped[6] = f']'
        self.placeText()


    def convertTrans(self, tag):
        if self.word_unwrapped[1] != '':
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