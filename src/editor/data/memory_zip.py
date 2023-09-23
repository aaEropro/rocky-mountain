import io
import zipfile
import copy

class InMemoryZip:
    '''
        extracts a zip into the memory.
    '''
    def __init__(self, path_to_zip):
        self.path_to_zip = path_to_zip
        self.file_data = {}

        # Load zip contents into memory
        with open(path_to_zip, 'rb') as f:
            with zipfile.ZipFile(f, 'r') as z:
                for name in z.namelist():
                    self.file_data[name] = z.read(name)


    def getFileNames(self) -> list[str]:
        ''' returns the file names inside the archive. '''
        return self.file_data.keys()


    def getFileContents(self, file_name, default=None, mode='file-like', encoding='utf-8'):
        ''' returns the contents of the file file_name. if there is no such file, return default. '''
        print(self.file_data.keys())

        contents = copy.deepcopy(self.file_data.get(file_name, default))

        if mode == 'file-like':    # makes the contents file-like, ie breaks them into lines 
            contents = contents.splitlines()
        elif mode == 'bytes':    # the contents are read as bytes, so do nothing
            pass
        elif mode == 'string':
            if type(contents) is not str:
                contents = contents.decode(encoding)
            contents = contents.replace('\r', '')
        else:
            raise TypeError('.getFileContents accepted modes are "bytes", "file-like".')
        
        return contents


    def setFileContents(self, file_name:str, data):
        ''' sets the contents of the file_name as data. '''
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.file_data[file_name] = data


    def deleteFile(self, file_name:str) -> None:
        ''' removes the specified file. '''
        self.file_data.pop(file_name, None)



    def save(self):
        ''' saves the archive. '''
        # Create a new in-memory byte stream
        zip_stream = io.BytesIO()

        # Create a new zip file in this stream
        with zipfile.ZipFile(zip_stream, 'w') as z:
            for name, data in self.file_data.items():
                z.writestr(name, data)

        # Save the in-memory zip to disk
        with open(self.path_to_zip, 'wb') as f:
            f.write(zip_stream.getvalue())


if __name__ == '__main__':
    instance = InMemoryZip(r'C:\Users\jovanni\Documents\GitHub\rocky-mountain\library\hilldiggers.rmb')
    print(instance.file_data)
