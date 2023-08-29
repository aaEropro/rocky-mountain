import os
from pathlib import Path
from configobj import ConfigObj
from addons.memory_zip import InMemoryZip



class BookMaster():
    '''
        this class is designed to handle an RMB files. it checks for integrity and validates the file. 
        it also provides navigation functionality.
    '''

    path_to_book = None
    splits_order = None

    current_split = None

################################## INITIALIZATION #################################################
    def __init__(self, path_to_book:str) -> None:
        ''' validate the file extension and extract it. '''

        if not os.path.isfile(path_to_book):    # check the file exists
            raise FileNotFoundError(f'the path {path_to_book} is not a file.')

        if not path_to_book.endswith('.rmb'):    # check the file is .rmb
            raise TypeError(f'expectiong an ".rmb" file but got a {path_to_book[-4:]} one.')

        self.path_to_book = path_to_book    # make the path global
        self.archive_name = Path(self.path_to_book).stem      # get the file's name
        
        self.unzipped_book = InMemoryZip(self.path_to_book)

        if not self.validateFileContents():
            raise RuntimeError(f'en error occured during file validation')
        self.loadVariousDataToMemory()


    def validateFileContents(self) -> bool:
        ''' verifies that all the necesary files exist. '''

        necessary_files = [    # list of necessary files
            'order.ini', 
            'setup.ini', 
        ]

        files_in_zip = self.unzipped_book.getFileNames()
        for file in necessary_files:
            if file not in files_in_zip:    # check if the file exists
                raise FileNotFoundError(f'necessary file {file} not found in the {self.archive_name}')

        return True


    def loadVariousDataToMemory(self) -> None:
        ''' loads various necessary file to memory '''

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
                raise FileNotFoundError(f'the {file} file from order.ini does not exist')

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
    def getStartpoint(self) -> (int, str):
        ''' returns the last open split and the last cursor position in that split'''

        last_read = self.setup['last-read']
        return last_read['cursor'], last_read['split']
    

    def getNextSplit(self, current_split:str) -> str|None:
        '''
            returns the next split, of one exists. if none exists, it returns None. 
            if the split name is not in in the split list, it returns the last item in the list.
        '''
        try: current_index = self.split_order.index(current_split)
        except: print('next not in the list'); current_index = len(self.split_order)-1
        if current_index+1 < len(self.split_order):
            return self.split_order[current_index+1]
        return None


    def getPrevSplit(self, current_split:str) -> str|None:
        '''
            returns the previous split, of one exists. if none exists, it returns None. 
            if the split name is not in in the split list, it returns the first item in the list.
        '''
        try: current_index = self.split_order.index(current_split)
        except: print('prev not in the list'); current_index = 0
        if current_index-1 >= 0:
            return self.split_order[current_index-1]
        return None
    

    def splitExists(self, split_name:str) -> bool:
        ''' returns 'True' if the split exists, else 'False'. '''
        if split_name in self.split_order:
            return True
        return False
    
    
    def getSplitByIndex(self, index:int) -> str|None:
        ''' returns the name of the split with that index, or None if that index does not exist. '''
        if len(self.split_order) > 0:
            if index < 0:
                return self.getSplitByIndex(0)
            elif index >= len(self.split_order):
                return self.getSplitByIndex(len(self.split_order)-1)
            else:
                return self.split_order[index]
        return None


    def getListOfSplits(self) -> list:
        ''' returns the list of splits existant in splits_order. '''
        return self.split_order
    

    def getListOfAllSplits(self) -> (list, list):
        ''' returns a tuple of 2 lists: first the split_order, second all other splits not in split_order. '''
        return self.split_order, self.split_not_present_in_order


    def getContentsOfSplit(self, split_name:str) -> str:
        contents = self.unzipped_book.getFileContents(split_name, '', mode='string')
        return contents


    def removeSpecificSplit(self, split_name:str) -> None:    # removes a split from order
        if split_name not in self.split_order:
            print('removeSpecificSplit return bypass')
            return
        self.split_order.remove(split_name)
        self.split_not_present_in_order.append(split_name)


    def restoreSpecificSplit(self, split_name:str) -> None:    # restores a split from order
        if (split_name in self.split_order) or (split_name not in self.split_not_present_in_order):
            print('resotreSpecificSplit return bypass')
            return
        self.split_order.append(split_name)
        self.split_not_present_in_order.remove(split_name)


    def deleteSpecificSplit(self, split_name:str) -> None:    # removes a split from order
        self.unzipped_book.deleteFile(split_name)
        self.split_not_present_in_order.remove(split_name)


    def setCurrentSplit(self, split_name:str) -> None:
        self.current_split = split_name


    def getCurrentSplit(self) -> str:
        return self.current_split


################################ ARCHIVE MANIPULATION #############################################
    def getArchiveName(self) -> str:
        ''' rerturns the name of the archive. '''
        return self.archive_name


    def write(self, split_name:str, split_contents:str) -> None:
        ''' writes the split_contents to split_name. '''
        split_contents = split_contents.replace('\n', '\n\n')
        self.unzipped_book.setFileContents(split_name, split_contents)


    def close(self, cursor:int = 0, split:str|None = None):
        ''' makes the necessaty saves to the data before closing archive. '''
        if split is None:     # fallback if split cannot be provided
            split = self.split_order[0]
        self.setup['last-read']['split'] = split
        self.setup['last-read']['cursor'] = cursor
        setup_ini_content = '\n'.join(self.setup.write())
        self.unzipped_book.setFileContents('setup.ini', setup_ini_content)

        self.order['files-order'] = self.split_order
        order_ini_content = '\n'.join(self.order.write())
        self.unzipped_book.setFileContents('order.ini', order_ini_content)

        self.unzipped_book.save()


if __name__ == '__main__':
    instance = BookMaster(r'C:\Users\jovanni\Documents\GitHub\rocky-mountain\library\hilldiggers.rmb')