from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class ResponsiveContextMenu():
    def __init__(self, editor:object) -> None:
        self.editor = editor
            
    def customContextMenu(self, event, word_unwrapped, position_when_clicked) -> None:
        context_menu = QMenu(self.editor)
        context_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid black;
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

        #::: tag menu
        tag_menu = QMenu('tags', context_menu)
        context_menu.addMenu(tag_menu)

        #::: transmission menu
        transmission_menu = QMenu('transmission', context_menu)
        context_menu.addMenu(transmission_menu)

        #::: others menu
        others_menu = QMenu('others', context_menu)
        context_menu.addMenu(others_menu)

        #::: cite menu
        cite_menu = QMenu('cite', others_menu)
        others_menu.addMenu(cite_menu)

        add_cite_d_tag = cite_menu.addAction('add d cite')
        add_cite_d_tag.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 'cite'))

        add_cite_l_tag = cite_menu.addAction('add l cite')
        add_cite_l_tag.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 'cite'))

        add_cite_r_tag = cite_menu.addAction('add r cite')
        add_cite_r_tag.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 'cite'))

        #:::
        to_lowercase = context_menu.addAction('lowercase')
        to_lowercase.triggered.connect(lambda: self.toLower(word_unwrapped, position_when_clicked))

        to_uppercase = context_menu.addAction('uppercase')
        to_uppercase.triggered.connect(lambda: self.toUpper(word_unwrapped, position_when_clicked))

        to_name = context_menu.addAction('name')
        to_name.triggered.connect(lambda: self.toName(word_unwrapped, position_when_clicked))


        #::: add dtag
        add_dtag_menu = QMenu('add dtag', tag_menu)
        add_dtag_menu.setEnabled(False)
        tag_menu.addMenu(add_dtag_menu)

        add_e_dtag_action = add_dtag_menu.addAction("add e dtag")
        add_e_dtag_action.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 'e'))

        add_a_dtag_action = add_dtag_menu.addAction("add a dtag")
        add_a_dtag_action.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 'a'))

        add_q_dtag_action = add_dtag_menu.addAction("add q dtag")
        add_q_dtag_action.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 'q'))

        add_t_dtag_action = add_dtag_menu.addAction("add t dtag")
        add_t_dtag_action.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 't'))

        add_f_dtag_action = add_dtag_menu.addAction("add f dtag")
        add_f_dtag_action.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 'f'))

        add_s_dtag_action = add_dtag_menu.addAction("add s dtag")
        add_s_dtag_action.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 's'))
        

        #::: add ltag
        add_ltag_menu = QMenu('add ltag', tag_menu)
        add_ltag_menu.setEnabled(False)
        tag_menu.addMenu(add_ltag_menu)

        add_e_ltag_action = add_ltag_menu.addAction("add e ltag")
        add_e_ltag_action.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 'e'))

        add_a_ltag_action = add_ltag_menu.addAction("add a ltag")
        add_a_ltag_action.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 'a'))

        add_q_ltag_action = add_ltag_menu.addAction("add q ltag")
        add_q_ltag_action.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 'q'))

        add_t_ltag_action = add_ltag_menu.addAction("add t ltag")
        add_t_ltag_action.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 't'))

        add_f_ltag_action = add_ltag_menu.addAction("add f ltag")
        add_f_ltag_action.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 'f'))

        add_s_ltag_action = add_ltag_menu.addAction("add s ltag")
        add_s_ltag_action.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 's'))


        #::: add rtag
        add_rtag_menu = QMenu('add rtag', tag_menu)
        add_rtag_menu.setEnabled(False)
        tag_menu.addMenu(add_rtag_menu)

        add_e_rtag_action = add_rtag_menu.addAction("add e rtag")
        add_e_rtag_action.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 'e'))

        add_a_rtag_action = add_rtag_menu.addAction("add a rtag")
        add_a_rtag_action.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 'a'))

        add_q_rtag_action = add_rtag_menu.addAction("add q rtag")
        add_q_rtag_action.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 'q'))

        add_t_rtag_action = add_rtag_menu.addAction("add t rtag")
        add_t_rtag_action.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 't'))

        add_f_rtag_action = add_rtag_menu.addAction("add f rtag")
        add_f_rtag_action.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 'f'))

        add_s_rtag_action = add_rtag_menu.addAction("add s rtag")
        add_s_rtag_action.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 's'))


        #::: remove dtag
        remove_dtag_action = tag_menu.addAction("remove dtag")
        remove_dtag_action.setEnabled(False)
        remove_dtag_action.triggered.connect(lambda: self.removeDTag(word_unwrapped, position_when_clicked))

        
        #::: remove ltag
        remove_ltag_action = tag_menu.addAction("remove ltag")
        remove_ltag_action.setEnabled(False)
        remove_ltag_action.triggered.connect(lambda: self.removeLTag(word_unwrapped, position_when_clicked))


        #::: remove rtag
        remove_rtag_action = tag_menu.addAction("remove rtag")
        remove_rtag_action.setEnabled(False)
        remove_rtag_action.triggered.connect(lambda: self.removeRTag(word_unwrapped, position_when_clicked))

        #::: convert dtag
        convert_dtag_menu = QMenu('convert dtag', tag_menu)
        convert_dtag_menu.setEnabled(False)
        tag_menu.addMenu(convert_dtag_menu)

        convert_dtag_to_e = convert_dtag_menu.addAction('convert dtag to e')
        convert_dtag_to_e.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 'e'))

        convert_dtag_to_a = convert_dtag_menu.addAction('convert dtag to a')
        convert_dtag_to_a.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 'a'))

        convert_dtag_to_q = convert_dtag_menu.addAction('convert dtag to q')
        convert_dtag_to_q.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 'q'))

        convert_dtag_to_s = convert_dtag_menu.addAction('convert dtag to s')
        convert_dtag_to_s.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 's'))

        convert_dtag_to_t = convert_dtag_menu.addAction('convert dtag to t')
        convert_dtag_to_t.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 't'))

        convert_dtag_to_f = convert_dtag_menu.addAction('convert dtag to f')
        convert_dtag_to_f.triggered.connect(lambda: self.addDTag(word_unwrapped, position_when_clicked, 'f'))


        #::: convert ltag
        convert_ltag_menu = QMenu('convert ltag', tag_menu)
        convert_ltag_menu.setEnabled(False)
        tag_menu.addMenu(convert_ltag_menu)

        convert_ltag_to_e = convert_ltag_menu.addAction('convert ltag to e')
        convert_ltag_to_e.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 'e'))

        convert_ltag_to_a = convert_ltag_menu.addAction('convert ltag to a')
        convert_ltag_to_a.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 'a'))

        convert_ltag_to_q = convert_ltag_menu.addAction('convert ltag to q')
        convert_ltag_to_q.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 'q'))

        convert_ltag_to_t = convert_ltag_menu.addAction('convert ltag to t')
        convert_ltag_to_t.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 't'))

        convert_ltag_to_f = convert_ltag_menu.addAction('convert ltag to f')
        convert_ltag_to_f.triggered.connect(lambda: self.addLTag(word_unwrapped, position_when_clicked, 'f'))

        #::: convert rtag
        convert_rtag_menu = QMenu('convert rtag', tag_menu)
        convert_rtag_menu.setEnabled(False)
        tag_menu.addMenu(convert_rtag_menu)

        convert_rtag_to_e = convert_rtag_menu.addAction('convert rtag to e')
        convert_rtag_to_e.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 'e'))

        convert_rtag_to_a = convert_rtag_menu.addAction('convert rtag to a')
        convert_rtag_to_a.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 'a'))

        convert_rtag_to_q = convert_rtag_menu.addAction('convert rtag to q')
        convert_rtag_to_q.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 'q'))

        convert_rtag_to_t = convert_rtag_menu.addAction('convert rtag to t')
        convert_rtag_to_t.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 't'))

        convert_rtag_to_f = convert_rtag_menu.addAction('convert rtag to f')
        convert_rtag_to_f.triggered.connect(lambda: self.addRTag(word_unwrapped, position_when_clicked, 'f'))




        #::: add dtransmission
        add_dtransmission_action = transmission_menu.addAction("add dtransmission")
        add_dtransmission_action.setEnabled(False)
        add_dtransmission_action.triggered.connect(lambda: self.addDTransmission(word_unwrapped, position_when_clicked))
        

        #::: add ltransmission
        add_ltransmission_action = transmission_menu.addAction("add ltransmission")
        add_ltransmission_action.setEnabled(False)
        add_ltransmission_action.triggered.connect(lambda: self.addLTransmission(word_unwrapped, position_when_clicked))


        #::: add rtansmission
        add_rtransmission_action = transmission_menu.addAction("add rtansmission")
        add_rtransmission_action.setEnabled(False)
        add_rtransmission_action.triggered.connect(lambda: self.addRTransmission(word_unwrapped, position_when_clicked))


        #::: remove dtransmission
        remove_dtransmission_action = transmission_menu.addAction("remove dtransmission")
        remove_dtransmission_action.setEnabled(False)
        remove_dtransmission_action.triggered.connect(lambda: self.removeDTransmission(word_unwrapped, position_when_clicked))

        
        #::: remove ltransmission
        remove_ltransmission_action = transmission_menu.addAction("remove ltransmission")
        remove_ltransmission_action.setEnabled(False)
        remove_ltransmission_action.triggered.connect(lambda: self.removeLTransmission(word_unwrapped, position_when_clicked))


        #::: remove rtansmission
        remove_rtransmission_action = transmission_menu.addAction("remove rtansmission")
        remove_rtransmission_action.setEnabled(False)
        remove_rtransmission_action.triggered.connect(lambda: self.removeRTransmission(word_unwrapped, position_when_clicked))



        #::: logic
        if word_unwrapped[2] == '' and word_unwrapped[4] == '':
            add_dtag_menu.setEnabled(True)
        if word_unwrapped[2] == '':
            add_ltag_menu.setEnabled(True)
        if word_unwrapped[2] == '':
            add_rtag_menu.setEnabled(True)
        if word_unwrapped[2] != '' and word_unwrapped[4] != '':
            remove_dtag_action.setEnabled(True)
            convert_dtag_menu.setEnabled(True)
            convert_ltag_menu.setEnabled(True)
            convert_rtag_menu.setEnabled(True)
        if word_unwrapped[2] != '':
            remove_ltag_action.setEnabled(True)
            convert_ltag_menu.setEnabled(True)
        if word_unwrapped[4] != '':
            remove_rtag_action.setEnabled(True)
            convert_rtag_menu.setEnabled(True)
        

        if word_unwrapped[1] == '' and word_unwrapped[6] == '':
            add_dtransmission_action.setEnabled(True)
            add_ltransmission_action.setEnabled(True)
            add_rtransmission_action.setEnabled(True)
        if word_unwrapped[1] == '':
            add_ltransmission_action.setEnabled(True)
        if word_unwrapped[6] == '':
            add_rtransmission_action.setEnabled(True)

        if word_unwrapped[1] != '' and word_unwrapped[6] != '':
            remove_dtransmission_action.setEnabled(True)
            remove_ltransmission_action.setEnabled(True)
            remove_rtransmission_action.setEnabled(True)
        if word_unwrapped[1] != '':
            remove_ltransmission_action.setEnabled(True)
        if word_unwrapped[6] != '':
            remove_rtransmission_action.setEnabled(True)
        
        context_menu.exec_(event.globalPos())
        self.editor.setFocus()


    def addDTag(self, word_unwrapped, position_when_clicked, tag):
        word = word_unwrapped[0] + word_unwrapped[1] + f'<{tag}>' + word_unwrapped[3] + f'</{tag}>' + word_unwrapped[5] + word_unwrapped[6] + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def addLTag(self, word_unwrapped, position_when_clicked, tag):
        word = word_unwrapped[0] + word_unwrapped[1] + f'<{tag}>' + word_unwrapped[3] + word_unwrapped[4] + word_unwrapped[5] + word_unwrapped[6] + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()

    
    def addRTag(self, word_unwrapped, position_when_clicked, tag):
        word = word_unwrapped[0] + word_unwrapped[1] + word_unwrapped[1] + word_unwrapped[3] + f'</{tag}>' + word_unwrapped[5] + word_unwrapped[6] + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def removeDTag(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + word_unwrapped[1] + '' + word_unwrapped[3] + '' + word_unwrapped[5] + word_unwrapped[6] + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def removeLTag(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + word_unwrapped[1] + '' + word_unwrapped[3] + word_unwrapped[4] + word_unwrapped[5] + word_unwrapped[6] + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def removeRTag(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + word_unwrapped[1] + word_unwrapped[2] + word_unwrapped[3] + '' + word_unwrapped[5] + word_unwrapped[6] + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def addDTransmission(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + '[h|' + word_unwrapped[2] + word_unwrapped[3] + word_unwrapped[4] + word_unwrapped[5] + ']' + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def addLTransmission(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + '[h|' + word_unwrapped[2] + word_unwrapped[3] + word_unwrapped[4] + word_unwrapped[5] + word_unwrapped[6] + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def addRTransmission(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + word_unwrapped[1] + word_unwrapped[2] + word_unwrapped[3] + word_unwrapped[4] + word_unwrapped[5] + ']' + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def removeDTransmission(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + '' + word_unwrapped[2] + word_unwrapped[3] + word_unwrapped[4] + word_unwrapped[5] + '' + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def removeLTransmission(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + '' + word_unwrapped[2] + word_unwrapped[3] + word_unwrapped[4] + word_unwrapped[5] + word_unwrapped[6] + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def removeRTransmission(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + word_unwrapped[1] + word_unwrapped[2] + word_unwrapped[3] + word_unwrapped[4] + word_unwrapped[5] + '' + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()
    

    def toUpper(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + word_unwrapped[1] + word_unwrapped[2] + word_unwrapped[3].upper() + word_unwrapped[4] + word_unwrapped[5] + word_unwrapped[6] + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def toLower(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + word_unwrapped[1] + word_unwrapped[2] + word_unwrapped[3].lower() + word_unwrapped[4] + word_unwrapped[5] + word_unwrapped[6] + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()


    def toName(self, word_unwrapped, position_when_clicked):
        word = word_unwrapped[0] + word_unwrapped[1] + word_unwrapped[2] + word_unwrapped[3].title() + word_unwrapped[4] + word_unwrapped[5] + word_unwrapped[6] + word_unwrapped[7] + word_unwrapped[8] + word_unwrapped[9]
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()
        cursor.setPosition(position_when_clicked)
        # print(cursor.position())
        self.editor.setTextCursor(cursor)
        cursor.insertText(word+' ')
        self.editor.setFocus()