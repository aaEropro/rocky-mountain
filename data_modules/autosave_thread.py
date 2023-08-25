from PySide6.QtCore import *
import threading


class AutoSaveThread(QThread):
    """
        creates a separate thread for saving the contents of the editor.
    """
    print_message_to_status_bar = Signal(str, object)

    current_split = None

    bookmaster = None

    def __init__(self, editor_instance:object):
        super().__init__()
        self.editor_instance = editor_instance

        self.internal_timer = QTimer(self)
        self.internal_timer.timeout.connect(self.save)


    def run(self):
        self.exec()


    def setBookmaster(self, bookmaster:object) -> None:
        """sets the bookmaster"""
        self.bookmaster = bookmaster


    def activate(self, time_skip:int=6000) -> None:    # activate the timer
        """activate the internal timer"""
        
        print(threading.get_ident())
        if self.bookmaster is None:
            self.print_message_to_status_bar.emit('Error: bookmaster not set!', None)
            # print('emmited')
            return
        self.internal_timer.start(time_skip)
        print('activated timer')


    @Slot()
    def deactivate(self) -> None:    # deactivates the timer
        """deactivates the internal timer."""
        self.internal_timer.stop()
        # print('deactivated timer')


    @Slot(str)
    def changeSplit(self, split_name:str) -> None:    # change the split
        """changes the location of the save. it requires the file name"""
        self.current_split = split_name
        self.print_message_to_status_bar.emit(f'changed split to {self.current_split}', 1500)


    def save(self):    # save the split
        """saves to the file"""
        if self.current_split is None:
            return

        try:
            self.bookmaster.write(self.current_split, self.editor_instance.toPlainText())
            self.print_message_to_status_bar.emit(f'succesfully saved!', 1500)
        except Exception as e:
            self.print_message_to_status_bar.emit(str(e), None)
            pass


