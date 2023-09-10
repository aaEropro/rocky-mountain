from PySide6.QtCore import Signal, QEvent, QPoint
from PySide6.QtGui import Qt, QTextBlockFormat, QTextDocument, QTextCursor, QTouchEvent
from PySide6.QtWidgets import QTextEdit

from src.editor.data.gmd_parser import GMDParser
from src.editor.data import unwrapper

from src.editor.ui.responsive_context_menu_2 import ResponsiveContextMenu



class BookEditor(QTextEdit):
    '''
        custom editor for books.
    '''
    _start_touch_point = None
    _read_only = False
    _tablet_mode = False
    _context = False

    context_btn = None

    presence_detection_singnal = Signal()


    def __init__(self, master):
        super().__init__(master)

        self.setAttribute(Qt.WA_AcceptTouchEvents, True)    # set the flag to accept touch control
        self.viewport().installEventFilter(self)    # install event filter on textEdit viewport

        self.responsive_context_menu = ResponsiveContextMenu(self)    # initiate the responsive context menu
        self.gmd_parser = GMDParser()    # initiate the GMD parser

        self.block_format = QTextBlockFormat()
        self.block_format.setTextIndent(30)


        # with open(os.path.join('editor', 'setup_files', 'book_editor_dark_mode.css')) as file:
        #     self.book_editor_dark_mode_styling = file.read()
        # self.setStyleSheet(self.book_editor_dark_mode_styling)


    def setTextContents(self, contents:str, cursor_position:int = 0, scroll_position:int=None) -> None:    # load text to editor
        ''' sets contents inside the editor. '''

        cursor_position = int(cursor_position)
        if cursor_position > len(contents)-1:    # verify the cursor position to be valid
            cursor_position = 0

        html_body = self.gmd_parser.parseDocument(contents)    # add HTML to GMD file

        try: self.textChanged.disconnect(self.onTextChanged)    # disconnect the text changed signal
        except RuntimeError: pass    # will be raised if it's not connected

        document = QTextDocument()    # create a document
        document.setHtml(html_body)    # place the HTML text

        cursor = QTextCursor(document)
        cursor.movePosition(QTextCursor.Start)

        while True:    # set first line indent
            block_format = cursor.blockFormat()
            block_format.merge(self.block_format)
            cursor.setBlockFormat(block_format)
            
            if cursor.block().next().isValid():
                cursor.movePosition(QTextCursor.NextBlock)
            else:
                break    # if there is no next block, break

        self.clear()    # clear the textEdit
        self.setDocument(document)    # set the new document
        cursor = self.textCursor()
        cursor.setPosition(cursor_position)    # set the cursor on the new possition
        self.setTextCursor(cursor)

        if (scroll_position is not None) and (0 <= scroll_position <= 100):
            vertical_scrollbar = self.verticalScrollBar()
            vertical_scrollbar.setValue(scroll_position)  # set scrollbar position
            self.moveCursorToTheTopLeft()

        self.textChanged.connect(self.onTextChanged)    # reconnect the text changed signal


    def reloadCurrentText(self) -> None:
        ''' reloads the contents currently displayed. '''

        contents = self.toPlainText().replace('\n', '\n\n')    # get the current contents
        cursor_position = self.textCursor().position()    # get the current cursor index
        scroll_position = self.verticalScrollBar().value()    # get the scrollbar position
        self.setTextContents(contents, cursor_position, scroll_position)


    def onTextChanged(self) -> None:    # update the HTML in the paragraph
        self.textChanged.disconnect(self.onTextChanged)    # disconnect immediately to avoid recursion
        cursor = self.textCursor()   # get the current cursor position for reference
        cursor_pos = cursor.position()
        cursor.movePosition(QTextCursor.StartOfBlock)    # select the paragraph under the cursor 
                                                         # and run it trough the GMD parser, then replace it.
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        paragraph_text = cursor.selectedText()
        to_html_paragraph_text = self.gmd_parser.parse_para(paragraph_text)
        cursor.removeSelectedText()
        cursor.insertHtml(to_html_paragraph_text)
        cursor.setPosition(cursor_pos)    # set the cursor to the old position. it should not give an error 
                                          # because the parser only adds HTML tags, which are not taken into 
                                          # account when calculating the index position of the cursor in the 
                                          # plain text
        block_format = cursor.blockFormat()
        block_format.merge(self.block_format)
        cursor.setBlockFormat(block_format)    # force an update on the block format
        self.setTextCursor(cursor)
        self.textChanged.connect(self.onTextChanged)    # reconnect after making the changes


################################## UNDER CURSOR ###################################################
    def getParagraphData(self):
        ''' get the paragraph under the cursor. '''
        cursor = self.textCursor()

        cursor_global_start_position = cursor.position()
        cursor_paragraph_start_position = cursor.positionInBlock()

        cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        paragraph_under_cursor = cursor.selectedText()

        cursor.setPosition(cursor_global_start_position)

        return cursor_paragraph_start_position, paragraph_under_cursor


    def getWordUnderCursor(self, index, para):
        ''' get the worrd under the cursor. '''
        para_lenght = len(para)
        string_before = ''
        string_after = ''
        index_before = index-1
        index_after = index

        while index_before >= 0 and ((para[index_before] != ' ') and (para[index_before] != '\n')):
            string_before = para[index_before] + string_before
            index_before -= 1

        while index_after < para_lenght and ((para[index_after] != ' ') and (para[index_after] != '\n')):
            string_after += para[index_after]
            index_after += 1

        return string_before+string_after, len(string_before)


    def processWord(self, event):
        ''' split the word in it's relevant parts. '''
        cursor_paragraph_start_position, paragraph_under_cursor = self.getParagraphData()
        word, position_in_word = self.getWordUnderCursor(cursor_paragraph_start_position, paragraph_under_cursor)
        word_unwrapped = unwrapper.unwrap(word)
        print(word_unwrapped)

        cursor = self.textCursor()    # get the initial cursor position
        clicked_position = cursor.position()

        start = clicked_position-position_in_word     # select the word under the cursor
        cursor.setPosition(clicked_position-position_in_word, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(word))
        self.setTextCursor(cursor)
        
        self.responsive_context_menu.customContextMenu(event, word_unwrapped, start)    # initiate context menu

        cursor.clearSelection()    # reset the cursor position
        cursor.setPosition(clicked_position)
        self.setTextCursor(cursor)


################################## EVENTS #########################################################
    def eventFilter(self, source, event):    # event filter for buttons of mouse clickes
        ''' add custome behaviour for mouse button clickes. '''

        if event.type() == QEvent.MouseButtonPress:

            if event.button() == Qt.LeftButton:
                self.presence_detection_singnal.emit()
                if self._context:
                    cursor = self.cursorForPosition(event.pos())    # get cursor at mouse click position
                    self.setTextCursor(cursor)    # update the cursor position
                    self.processWord(event)
                    if self._tablet_mode:
                        self.toggleContextHelp(self.context_btn, bypass=True)
                    return True    # event is handled

            elif event.button() == Qt.RightButton:
                self.presence_detection_singnal.emit()
                cursor = self.cursorForPosition(event.pos())    # get cursor at mouse click position
                self.setTextCursor(cursor)    # update the cursor position
                self.processWord(event)
                return True

        return super().eventFilter(source, event)
    
    
    def event(self, event):    # event filter for touch
        ''' add custome behaviour for touch events. '''

        if event.type() == QTouchEvent.TouchBegin:
            self._start_touch_point = event.touchPoints()[0].startPos().y()
            self.presence_detection_singnal.emit()
            return True

        elif event.type() == QTouchEvent.TouchUpdate and self._start_touch_point is not None:
            delta = event.touchPoints()[0].pos().y() - self._start_touch_point
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta)
            self.moveCursorToTheTopLeft()
            return True

        elif event.type() == QTouchEvent.TouchEnd:
            self._start_touch_point = None
            return True

        return super().event(event)
    

    def wheelEvent(self, event):    # extension for mousewheel event
        ''' ensure that the cursor remains on the viewport when scrolling. '''

        super().wheelEvent(event)    # call the base class wheelEvent to retain default behavior
        self.moveCursorToTheTopLeft()
        self.presence_detection_singnal.emit()
        
        
    def moveCursorToTheTopLeft(self) -> None:   # keeps the cursor on the top-left while scrolling
        ''' has built-in safeguards for not moving the cursor if it still is inside the visible area. '''
    
        top_left_cursor = self.cursorForPosition(QPoint(0,0))
        bottom_right_cursor = self.cursorForPosition(QPoint(self.viewport().width(), self.viewport().height()))
        current_cursor = self.textCursor()
        if (top_left_cursor.position() > current_cursor.position()) or (bottom_right_cursor.position() < current_cursor.position()):
            self.setTextCursor(top_left_cursor)


################################## TOGGLES ########################################################
    def toggleContextHelp(self, button, bypass = False):    # toggle context help mode
        if button is not None:
            if bypass and self._context:     # verify for bypass from second mouse click
                self._context = False
                self.context_btn.setChecked(False)
            else:
                self.context_btn = button
                if button.isChecked():
                    self._context = True
                else:
                    self._context = False
        self.setFocus()


    def toggleReadOnly(self, button):    # toggle read only mode
        if button.isChecked():
            self.setReadOnly(True)
            self.setTextInteractionFlags(Qt.NoTextInteraction)
            self._read_only = True
        else:
            self.setReadOnly(False)
            self.setTextInteractionFlags(Qt.TextEditorInteraction)
            self._read_only = False
        self.setFocus()


    def toggleTabletMode(self, button:object) -> None:    # toggle the tablet mode
        if button.isChecked():
            self._tablet_mode = True
        else:
            self._tablet_mode = False
        self.setFocus()