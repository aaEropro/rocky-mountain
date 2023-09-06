from PySide6.QtCore import *
from PySide6.QtWidgets import *
from editor.data_modules.book_master import BookMaster



class AutoSave(QObject):
    """
        timer for saving the contents of the editor.
    """
    print_message_to_status_bar = Signal(str, object)



    def __init__(self, editor_instance:QTextEdit):
        super().__init__()
        self.editor_instance = editor_instance
        
        self.event_happened = False
        self.current_split = None
        self.bookmaster = None

        self.internal_timer = QTimer()
        # self.internal_timer.timeout.connect(self.save)


    def setBookmaster(self, bookmaster:BookMaster) -> None:
        """sets the bookmaster"""
        self.bookmaster = bookmaster


    def activate(self, time_skip:int=20000) -> None:    # activate the timer
        """activate the internal timer"""
        self.time_skip = time_skip

        if self.bookmaster is None:
            self.print_message_to_status_bar.emit('Error: bookmaster not set!', None)
            return
        self.internal_timer.singleShot(self.time_skip, self.save)


    def eventHappenes(self) -> None:
        self.event_happened = True


    def deactivate(self) -> None:    # deactivates the timer
        """deactivates the internal timer."""
        self.internal_timer.stop()


    def changeSplit(self, split_name:str) -> None:    # change the split
        """changes the location of the save. it requires the file name"""
        self.current_split = split_name
        self.print_message_to_status_bar.emit(f'changed split to {self.current_split}', 1500)


    def save(self):    # save the split
        ''' saves the contents of the editor. '''
        if self.current_split is None:
            return

        try:
            self.bookmaster.write(self.current_split, self.editor_instance.toPlainText())
            self.print_message_to_status_bar.emit(f'succesfully saved!', 1500)
        except Exception as e:
            self.print_message_to_status_bar.emit(str(e), None)
            pass

        if self.event_happened:
            self.internal_timer.singleShot(self.time_skip, self.save)


