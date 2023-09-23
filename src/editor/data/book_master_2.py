import os
from pathlib import Path
from configobj import ConfigObj
from PySide6.QtCore import QTimer, QObject, Signal, Slot
import json
import time
import sys

from addons.memory_zip import InMemoryZip

from src.editor.data.split_master import OrderHolder, Split, SplitState


VERSION = 2.0



class BookMaster(QObject):
    '''
        this class is designed to handle an RMB files. it checks for integrity and validates the file. 
        it also provides navigation functionality.
    '''

    def __init__(self, parent=None) -> None:
        ''' validate the file extension and extract it. '''
        super().__init__(parent)

        self.path_to_book = None
        self.split_order = None
        self.current_split = None
        self.unzipped_book = None
        self.first_load = True
        self.initReadtimeTimer()
        self.initArchiveTimer()
        self.initSplitTimer()

    def open(self, path_to_book:str):
        if not os.path.isfile(path_to_book):    # check the file exists
            raise Exception(f'the path {path_to_book} is not a file.')

        if not path_to_book.endswith('.rmb'):    # check the file is .rmb
            raise Exception(f'expectiong an ".rmb" file but got a {path_to_book[-4:]} one.')

        self.path_to_book = path_to_book    # make the path global
        self.archive_name = Path(self.path_to_book).stem      # get the file's name
        
        self.unzipped_book = InMemoryZip(self.path_to_book)

        self.validateContents()
        self.loadData()
        self.setStartpoint()
        self.activateReadtimeTimer()
        self.activateArchiveTimer()


################################## ARCHIVE VALIDATION #############################################
    def validateContents(self) -> bool:
        ''' verifies that all the necesary files exist. '''

        necessary_files = [    # list of necessary files
            'order.ini', 
            'setup.ini', 
        ]

        files_in_zip = self.unzipped_book.getFileNames()
        for file in necessary_files:
            if file not in files_in_zip:    # check if the file exists
                raise Exception(f'necessary file {file} not found in the {self.archive_name}')


################################## ARCHIVE LOADING ################################################
    def loadData(self) -> None:
        ''' loads necessary file to memory '''
        read_times_content = self.unzipped_book.getFileContents('read_times.json', mode='string')
        self.old_read_intervals = json.loads(read_times_content)['read-times']

        setup_ini_content = self.unzipped_book.getFileContents('setup.ini')
        self.setup = ConfigObj(setup_ini_content)

        order_ini_content = self.unzipped_book.getFileContents('order.ini')
        self.order = ConfigObj(order_ini_content)
        inorder_list = self.order['inorder']
        outorder_list = self.order['outorder']
        deleted_list = self.order['deleted']

        self.order_holder = OrderHolder()
        for item in inorder_list:
            obj = Split(item)
            self.order_holder.addSplit(obj, SplitState.INORDER)
        for item in outorder_list:
            obj = Split(item)
            self.order_holder.addSplit(obj, SplitState.OUTORDER)
        for item in deleted_list:
            obj = Split(item)
            self.order_holder.addSplit(obj, SplitState.DELETED)


################################ SPLIT CHECKING ###############################################
    def isNext(self) -> bool:
        ''' returns `True` if there is a next split, else `False`. '''
        return self.order_holder.isNext(self.current_split)

    def isPrevious(self) -> bool:
        ''' returns `True` if there is a previous split, else `False`. '''
        return self.order_holder.isPrevious(self.current_split)
    
    def isInorder(self, filename:str) -> bool:
        ''' returns `True` if the provided filename is in the ordered list, else `False`. '''
        state = self.order_holder.getState(filename)
        if state == SplitState.INORDER:
            return True
        return False


################################## SPLIT SETTING ##################################################
    def setStartpoint(self) -> None:
        last_read_split = self.setup['last-read']['split']
        self.current_split = last_read_split

    def setNext(self):
        self.split_timer.stop()
        self.saveSplit()
        next = self.order_holder.getNext(self.current_split)
        self.current_split = next
        print(f'stopped timer, split switch to next, current {self.current_split}')

    def setPrevious(self):
        self.split_timer.stop()
        self.saveSplit()
        previous = self.order_holder.getPrevious(self.current_split)
        self.current_split = previous
        print(f'stopped timer, split switch to previous, current {self.current_split}')

    def setSplit(self, split_name:str):
        self.split_timer.stop()
        self.saveSplit()
        self.current_split = split_name
        print(f'stopped timer, split switch to custom, current {self.current_split}')

    def setInorder(self, inorder):
        for index, item in enumerate(inorder):
            self.order_holder.setState(item, SplitState.INORDER)
            self.order_holder.atSpot(item, index)

    def setOutorder(self, outorder):
        for item in outorder:
            self.order_holder.setState(item, SplitState.OUTORDER)

    def setDeleted(self, deleted):
        for item in deleted:
            self.order_holder.setState(item, SplitState.DELETED)


################################## SPLIT GETTING ##################################################
    def getOrdered(self) -> list:
        return self.order_holder.getInorder()
    
    def getFree(self) -> list:
        return self.order_holder.getOutorder()
    
    def getAll(self) -> list[str]:
        ''' returns inorder list and outorder list. '''
        return self.order_holder.getInorder(), self.order_holder.getOutorder()

    def getCurrent(self):
        return self.current_split

    def getAtIndex(self, index:int) -> str|None:
        return self.order_holder.getAt(index)

################################## DATA SETTING ###################################################
    def setMetadata(self, metadata:dict):
        contents = self.unzipped_book.getFileContents(self.current_split, '', mode='string')
        json_dict = json.loads(contents)
        json_dict['metadata'] = metadata
        json_str = json.dumps(json_dict)
        self.unzipped_book.setFileContents(self.current_split, json_str)


################################## DATA GETTING ###################################################
    def getBody(self) -> str:
        print(f'get contents of split {self.current_split}')
        contents = self.unzipped_book.getFileContents(self.current_split, '', mode='string')
        json_dict = json.loads(contents)
        cursor = 0
        if self.first_load:
            cursor = int(self.setup['last-read']['cursor'])
            self.first_load = False
        return json_dict['body'], cursor
    
    def getMetadata(self) -> str:
        contents = self.unzipped_book.getFileContents(self.current_split, '', mode='string')
        json_dict = json.loads(contents)
        return json_dict['metadata']


################################## SPLIT TIMER ####################################################
    def initSplitTimer(self):
        self.split_timer = QTimer(self)
        self.split_timer.timeout.connect(self.saveSplit)
        self.split_timer.setSingleShot(True)

    def activateSplitTimer(self):
        self.split_timer.start(20000)
        print(f'timer activated on split {self.current_split}')

    def saveSplit(self):
        contents:str = self.parent().editor.toPlainText() # !!!!!!!! dont like that i have to link like this
        contents = contents.replace('\n', '\n\n')
        metadata = self.getMetadata()
        json_dict = {
            "metadata": metadata,
            "body": contents
        }
        json_str = json.dumps(json_dict)
        self.unzipped_book.setFileContents(self.current_split, json_str)
        print(f'saved split {self.current_split}!')
        self.split_timer.start(20000)


################################## READTIME TIMERS ################################################
    def initReadtimeTimer(self):
        self.read_intervals_since_opened = []
        self.start_time = None
        self.warmup = False
        self.event_happened = False
        self.active_timer = False
        self.readtime_timer = QTimer(self)
        self.readtime_timer.timeout.connect(self.readtimeTimeout)
        self.readtime_timer.setSingleShot(True)

    def activateReadtimeTimer(self):
        self.warmup = True
        self.start_time = time.time()
        self.active_timer = True
        self.event_happened = False
        self.readtime_timer.start(120000)    # 2 min warmup
        print('readtime timer warmup activated.')

    def presenceDetected(self):
        if (not self.active_timer) and (self.path_to_book is not None):
            self.activateReadtimeTimer()
        else:
            self.event_happened = True
            # print('event happened')

    def readtimeTimeout(self):
        if self.warmup and self.event_happened:    # ended warmup and something happened inside the editor
            self.warmup = False
            self.event_happened = False
            self.readtime_timer.start(90000)    # 1.5 min pause between checks
            print('ended warmup, event(s) happened, continuing...')

        elif self.warmup and (not self.event_happened):    # ended warmup and nothing happened inside the editor
            self.active_timer = False
            self.warmup = False
            print('warmup failed, timeout.')

        elif self.event_happened:    # ended timer and something happened inside the editor
            self.event_happened = False
            self.readtime_timer.start(90000)
            print('event(s) happened, continuing...')

        else:    # ended timer and nothing happened inside the editor
            self.active_timer = False
            if self.start_time is not None:
                self.read_intervals_since_opened.append((self.start_time, time.time()))
                self.start_time = time.time()
            print(f'timeout, {self.read_intervals_since_opened}')

    def getReadtimeIntervals(self):
        if self.warmup:
            return []
        if self.active_timer:
            return [*self.read_intervals_since_opened, (self.start_time, time.time())]
        return self.read_intervals_since_opened


################################## ARCHIVE TIMER ##################################################
    def initArchiveTimer(self):
        self.archive_timer = QTimer(self)
        self.archive_timer.timeout.connect(self.saveArchive)
        self.archive_timer.setSingleShot(True)

    def activateArchiveTimer(self):
        self.archive_timer.start(60000)
        # print('activated archive timer!')

    def saveArchive(self):
        cursor_position = self.parent().editor.textCursor().position() # !!!!!!!! dont like that i have to link like this
        self.setup['last-read']['split'] = self.current_split
        self.setup['last-read']['cursor'] = cursor_position
        setup_ini_content = '\n'.join(self.setup.write())
        self.unzipped_book.setFileContents('setup.ini', setup_ini_content)

        self.order['files-order'] = self.split_order
        order_ini_content = '\n'.join(self.order.write())
        self.unzipped_book.setFileContents('order.ini', order_ini_content)

        read_intervals_since_opened = self.getReadtimeIntervals()
        merged_read_times = self.old_read_intervals+read_intervals_since_opened
        read_times_dict = {'read-times': merged_read_times}
        read_times_content = json.dumps(read_times_dict).encode('utf-8')
        self.unzipped_book.setFileContents('read_times.json', read_times_content)

        self.unzipped_book.save()
        self.archive_timer.start(60000)
        print('saved archive!')


##################################################################################################
    def close(self):
        print('closing bookmaster!')
        self.split_timer.stop()
        self.archive_timer.stop()
        self.readtime_timer.stop()

        if self.path_to_book is not None:
            self.saveSplit()
            self.saveArchive()

        self.deleteLater()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    instamce = BookMaster()
    instamce.open(r'C:\Users\jovanni\Desktop\lib\rajaniemi-hannu--the-fractal-prince.rmb')
    app.exec()