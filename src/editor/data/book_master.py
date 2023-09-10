import os
from pathlib import Path
from configobj import ConfigObj
from PySide6.QtCore import QTimer, QObject, Signal, Slot
import json
import time

from addons.memory_zip import InMemoryZip



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
        # print(self.old_read_intervals)

        setup_ini_content = self.unzipped_book.getFileContents('setup.ini')
        self.setup = ConfigObj(setup_ini_content)

        order_ini_content = self.unzipped_book.getFileContents('order.ini')
        self.order = ConfigObj(order_ini_content)
        files_existent_in_order = self.order['files-order']

        files_in_zip = self.unzipped_book.getFileNames()
        all_split_files = []
        for item in files_in_zip:
            if ('split' in item) and item.endswith('.gmd'):
                all_split_files.append(item)

        for file in files_existent_in_order:    # verify all the splits exist
            if file in files_in_zip:
                all_split_files = [item for item in all_split_files if item != file]    # removes the current file
            else:
                raise Exception(f'the {file} file from order.ini does not exist')

        self.split_not_present_in_order = []
        file_str = ''
        if len(all_split_files) > 0:
            for file in all_split_files:
                self.split_not_present_in_order.append(file)
                file_str += file + ', '
        if len(self.split_not_present_in_order) > 0:
            print(f'Warning: file(s) {file_str[:-2]} is not present in split order list. you should look into that.')
        self.split_order = files_existent_in_order    # load splits order to global memory


################################ SPLIT MANIPULATION ###############################################
    def setStartpoint(self) -> None:
        last_read_split = self.setup['last-read']['split']
        if last_read_split not in self.split_order:
            last_read_split = self.split_order[0]
        self.current_split = last_read_split
        # self.first_load = True
    
    def isNext(self):
        current_index = self.split_order.index(self.current_split)
        if current_index+1 < len(self.split_order):
            return True
        return False
    
    def isPrevious(self):
        current_index = self.split_order.index(self.current_split)
        if current_index-1 >= 0:
            return True
        return False
    
    def setNext(self):
        self.split_timer.stop()
        self.saveSplit()
        current_index = self.split_order.index(self.current_split)
        self.current_split = self.split_order[current_index+1]
        print(f'stopped timer, split switch to next, current {self.current_split}')

    def setPrevious(self):
        self.split_timer.stop()
        self.saveSplit()
        current_index = self.split_order.index(self.current_split)
        self.current_split = self.split_order[current_index-1]
        print(f'stopped timer, split switch to previous, current {self.current_split}')
    
    def setSplit(self, split_name:str):
        if (split_name not in self.split_order) and (split_name not in self.split_not_present_in_order):
            return
        self.split_timer.stop()
        self.saveSplit()
        self.current_split = split_name
        print(f'stopped timer, split switch to custom, current {self.current_split}')

    def getOrdered(self) -> list:
        return self.split_order
    
    def getFree(self) -> list:
        return self.split_not_present_in_order
    
    def getAll(self) -> list:
        return self.split_order, self.split_not_present_in_order
    
    def getBody(self) -> str:
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

    def setMetadata(self, metadata:dict):
        contents = self.unzipped_book.getFileContents(self.current_split, '', mode='string')
        json_dict = json.loads(contents)
        json_dict['metadata'] = metadata
        json_str = json.dumps(json_dict)
        self.unzipped_book.setFileContents(self.current_split, json_str)

    def getCurrent(self):
        return self.current_split

    def removeSpecificSplit(self, split_name:str) -> None:    # removes a split from order
        self.split_order.remove(split_name)
        self.split_not_present_in_order.append(split_name)

    def restoreSpecificSplit(self, split_name:str) -> None:    # restores a split from order
        self.split_order.append(split_name)
        self.split_not_present_in_order.remove(split_name)

    def deleteSpecificSplit(self, split_name:str) -> None:    # removes a split from order
        self.unzipped_book.deleteFile(split_name)
        self.split_not_present_in_order.remove(split_name)


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