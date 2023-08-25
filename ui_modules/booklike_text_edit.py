
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from ui_modules.responsive_context_menu import ResponsiveContextMenu
from data_modules.gmd_parser import GMDParser
from data_modules import unwrapper
from data_modules.autosave_thread import AutoSaveThread
from data_modules.book_master import BookMaster


class BooklikeTextEdit(QTextEdit):
    _start_touch_point = None
    _read_only = False
    _tablet_mode = False
    _context = False

    context_btn = None

    FILEPATH = None

    autosave:AutoSaveThread = None

    def __init__(self, master):
        super().__init__(master)

        self.setAttribute(Qt.WA_AcceptTouchEvents, True)    # set the flag to accept touch control
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)    # hide the scrollbar for book-like mode
        self.responsive_context_menu = ResponsiveContextMenu(self)    # initiate the responsive context menu
        self.viewport().installEventFilter(self)    # install event filter on textEdit viewport
        self.gmd_parser = GMDParser()    # initiate the GMD parser

        self.block_format = QTextBlockFormat()
        self.block_format.setTextIndent(30)



    def uploadFromFile(self, path:str, bookmaster:BookMaster, cursor_position:int = 0) -> None:    # load text to editor
        #: this funtion expects to be given a valid path for a GMD file and does not have 
        #: safeguards in place for dealing with invalid files
        #
        #: in the future i plan to implement an encoding verification step, but for now it 
        #: assumes it is using utf-8
        
        # self.autosave.setBookmaster(bookmaster)
        self.autosave.deactivate()    # deactivate the autosaves

        with open(path, encoding= 'utf-8', mode='r') as file:    # read the espective file
            body = file.read()
    
        if cursor_position > len(body)-1:    # verify the cursor position to be valid
            cursor_position = 0
        html_body = self.gmd_parser.parseDocument(body)    # add HTML to GMD file
        try:
            self.textChanged.disconnect(self.onTextChanged)    # disconnect the text changed signal
        except RuntimeError:    # will be raised if it's not connected
            pass

        document = QTextDocument()    # create a document
        document.setHtml(html_body)    # place the HTML text

        cursor = QTextCursor(document)
        cursor.movePosition(QTextCursor.End)

        one_time_bypass = False
        while (not cursor.atStart()) or (not one_time_bypass):    # loop over all the paragraphs and apply the indent
            if cursor.atStart():
                one_time_bypass = True
            block_format = cursor.blockFormat()
            block_format.merge(self.block_format)
            cursor.setBlockFormat(block_format)
            cursor.movePosition(QTextCursor.PreviousBlock)
            

        self.clear()    # clear the textEdit
        self.setDocument(document)    # set the new document
        cursor = self.textCursor()
        cursor.setPosition(cursor_position)    # set the cursor on the new possition
        self.setTextCursor(cursor)

        self.textChanged.connect(self.onTextChanged)    # reconnect the text changed signal

        self.autosave.changeSplit(bookmaster.getCurrentSplit())    # set current split
        self.autosave.activate()    # activate the autosave


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


    def getParagraphData(self):     # get the paragraph under the cursor
        cursor = self.textCursor()

        cursor_global_start_position = cursor.position()
        cursor_paragraph_start_position = cursor.positionInBlock()

        cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        paragraph_under_cursor = cursor.selectedText()

        cursor.setPosition(cursor_global_start_position)

        return cursor_paragraph_start_position, paragraph_under_cursor


    def getWordUnderCursor(self, index, para):  # get the word under the cursor
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


    def processWord(self, event):   # split the word in it's relevant parts
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


    def eventFilter(self, source, event):    # event filter for buttons of mouse clickes
        #: add custome behaviour for mouse button clickes

        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton and self._context:
                cursor = self.cursorForPosition(event.pos())    # get cursor at mouse click position
                self.setTextCursor(cursor)    # update the cursor position
                self.processWord(event)
                if self._tablet_mode:
                    self.toggleContextHelp(self.context_btn, bypass=True)
                return True    # event is handled
            elif event.button() == Qt.RightButton:
                cursor = self.cursorForPosition(event.pos())    # get cursor at mouse click position
                self.setTextCursor(cursor)    # update the cursor position
                self.processWord(event)
                return True
        return super(BooklikeTextEdit, self).eventFilter(source, event)
    
    
    def event(self, event):    # event filter for touch
        #: add custome behaviour for touch events

        if event.type() == QTouchEvent.TouchBegin:
            self._start_touch_point = event.touchPoints()[0].startPos().y()
            return True
        elif event.type() == QTouchEvent.TouchUpdate and self._start_touch_point is not None:
            delta = event.touchPoints()[0].pos().y() - self._start_touch_point
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta)
            self.moveCursorToTheTopLeft()
            return True
        elif event.type() == QTouchEvent.TouchEnd:
            self._start_touch_point = None
            return True
        return super(BooklikeTextEdit, self).event(event)
    

    def wheelEvent(self, event):    # extension for mousewheel event
        #: ensure that the cursor remains on the viewport when scrolling

        super(BooklikeTextEdit, self).wheelEvent(event)    # call the base class wheelEvent to retain default behavior
        self.moveCursorToTheTopLeft()
        
        
    def moveCursorToTheTopLeft(self) -> None:   # keeps the cursor on the top-left while scrolling
        #: has built-in safeguards for not moving the cursor if it still is inside the visible area
    
        top_left_cursor = self.cursorForPosition(QPoint(0,0))
        bottom_right_cursor = self.cursorForPosition(QPoint(self.viewport().width(), self.viewport().height()))
        current_cursor = self.textCursor()
        if (top_left_cursor.position() > current_cursor.position()) or (bottom_right_cursor.position() < current_cursor.position()):
            self.setTextCursor(top_left_cursor)


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