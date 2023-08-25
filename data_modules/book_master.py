import os
import zipfile
from pathlib import Path
from configobj import ConfigObj
import shutil

class BookMaster():
    #: this class is designed to handle an RMB file.
    #
    #: it checks for integrity and validates the file. 
    #: it also provides navigation functionality.

    path_to_book = None
    splits_order = None

    ERROR = False
 
    def __init__(self, received_path_to_book:str) -> None:
        # : validate the file extension and extract it to a temp folder.

        if not os.path.isfile(received_path_to_book):    # check the file exists
            raise FileNotFoundError(f'the path {received_path_to_book} is not a file.')
        if not received_path_to_book[-3:] == 'rmb':    # check the file is .rmb
            raise TypeError(f'expectiong an ".rmb" file but got a {received_path_to_book[-4:]} one.')
        self.path_to_book = received_path_to_book    # make the path global
        
        os.path.isdir('temp')       # verify temp folder exists

        self.rmb_file_filename = Path(self.path_to_book).stem      # get the file's name

        with zipfile.ZipFile(self.path_to_book, 'r') as zip_ref:       # unzip the file to temp
            zip_ref.extractall(os.path.join('temp', self.rmb_file_filename))

        if not self.validateFileContents(os.path.join('temp', self.rmb_file_filename)):
            raise RuntimeError(f'en error occured during file validation')
        self.loadVariousDataToMemory(os.path.join('temp', self.rmb_file_filename))


    def validateFileContents(self, path_to_temp_extracted_location:str) -> bool:
        #: this functin verifies that all the necesary files exist.

        necessary_filenames = [    # list of necessary files
            'order.ini', 
            'setup.ini', 
        ]

        for filename in necessary_filenames:
            if not os.path.isfile(os.path.join(path_to_temp_extracted_location, filename)):    # check if the file exists
                raise FileNotFoundError(f'necessary file {filename} not found in the {self.rmb_file_filename}')

        return True


    def loadVariousDataToMemory(self, path_to_temp_extracted_location:str) -> None:
        #: this function loades various necessary file to memory

        order = ConfigObj(os.path.join(path_to_temp_extracted_location, 'order.ini'))
        files_existent_in_order = order['files-order']

        all_split_files = []
        for item in os.listdir(path_to_temp_extracted_location):
            if os.path.isfile(os.path.join(path_to_temp_extracted_location, item)) and (('split' in item) and ('.gmd' in item)):
                all_split_files.append(item)

        for file in files_existent_in_order:    # verify all the splits exist
            if os.path.isfile(os.path.join(path_to_temp_extracted_location, file)):
                all_split_files = [item for item in all_split_files if item != file]    # removes the current file
            else:
                raise FileNotFoundError(f'the {file} file from order.ini does not exist')
        self.split_not_present_in_order = []
        if len(all_split_files) > 0:
            for file in all_split_files:
                self.split_not_present_in_order.append(file)
                print(f'Warning: file {file} is not present in split order list. you should look into that.')
        self.split_order = files_existent_in_order    # load splits order to global memory


    def close(self, cursor:int = 0, split:str|None = None):
        if self.ERROR:    # bypass the saving step in case of error
            print('entered error-driven closing bypass')
            return

        if not os.path.isdir(os.path.join('temp', self.rmb_file_filename)):
            raise FileNotFoundError(f'the extracted file {self.rmb_file_filename} not found in temp')
        
        if split is None:     # fallback if split cannot be provided
            split = self.split_order[0]

        setup = ConfigObj(os.path.join('temp', self.rmb_file_filename, 'setup.ini'))
        setup['last-read']['split'] = split
        setup['last-read']['cursor'] = cursor
        setup.write()

        order = ConfigObj(os.path.join('temp', self.rmb_file_filename, 'order.ini'))
        order['files-order'] = self.split_order
        order.write()
        
        os.remove(self.path_to_book)        # remove the original file

        with zipfile.ZipFile(self.path_to_book, 'w') as zipf:       # recreate the .rmb file
            for foldername, subfolders, files in os.walk(os.path.join('temp', self.rmb_file_filename)):
                for file in files:
                    # Create the full file path
                    file_path = os.path.join(foldername, file)
                    # Add the file to the zip
                    zipf.write(file_path, os.path.relpath(file_path, os.path.join('temp', self.rmb_file_filename)))

        shutil.rmtree(os.path.join('temp', self.rmb_file_filename), ignore_errors=True)    # remove the extracted .rmb from temp folder


    def getStartpoint(self) -> (int, str):
        config = ConfigObj(os.path.join('temp', self.rmb_file_filename, 'setup.ini'))
        last_read = config['last-read']
        return last_read['cursor'], last_read['split']
    

    def getNextSplit(self, current_split:str) -> str|None:
        try: current_index = self.split_order.index(current_split)
        except: print('next not in the list'); current_index = len(self.split_order)-1
        if current_index+1 < len(self.split_order):
            return self.split_order[current_index+1]
        return None


    def getPrevSplit(self, current_split:str) -> str|None:
        try: current_index = self.split_order.index(current_split)
        except: print('prev not in the list'); current_index = 0
        if current_index-1 >= 0:
            return self.split_order[current_index-1]
        return None
    

    def splitExists(self, split_name:str) -> bool:
        if split_name in self.split_order:
            return True
        return False
    
    
    def getSplitByIndex(self, index:int) -> str|None:
        if len(self.split_order) > 0:
            if index < 0:
                return self.getSplitByIndex(0)
            elif index >= len(self.split_order):
                return self.getSplitByIndex(len(self.split_order)-1)
            else:
                return self.split_order[index]
        return None


    def getListOfSplits(self) -> list:
        return self.split_order
    

    def getListOfAllSplits(self) -> (list, list):
        return self.split_order, self.split_not_present_in_order
    

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
        os.remove(os.path.join('temp', self.rmb_file_filename, split_name))        # deletes the split file
        self.split_not_present_in_order.remove(split_name)
        print(f'deleted split {split_name}')


    def write(self, split_name:str, split_contents:str) -> None:
        split_contents = split_contents.replace('\n', '\n\n')
        with open(os.path.join('temp', self.rmb_file_filename, split_name), encoding='utf-8', mode='w') as file:
            file.write(split_contents)
            file.close()
        

if __name__ == '__main__':
    instance = BookMaster(r'C:\Users\jovanniBoss\Desktop\test.rmb')
    instance.close()
    # print(instance.getStartpoint())
    instance.write('split_001.gmd', 'hello!')
    print(instance.getNextSplit('split_003.gmd'))
    # instance.getNextSplit('split_001.gmd')

        