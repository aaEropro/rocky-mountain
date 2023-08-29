import os
import io
import zipfile
import json
from configobj import ConfigObj


class LibraryMaster():
    '''
        manages the library and books.
    '''
    books_in_library = []
    covers_in_cache = []
    metadata = {}

    default_metadata = {
        "author-first-name": "None",
        "author-last-name": "None",

        "univers": "None",
        "series": "None",
        "volume": "None",
        "title": "None",

        "isbn-e": "None"
    }

    def __init__(self, library_path:str) -> None:
        if os.path.isdir(library_path):
            self.library_path = library_path
            self.cache_path = os.path.join(self.library_path, 'cache')
        else:
            raise FileNotFoundError(f'this is not a valid path: {library_path}')
        
        os.makedirs(self.cache_path, exist_ok=True)    # make sure the cache exists

        self.readMetadata()
        self.walkLibrary()
        self.walkCoverCache()


    def readMetadata(self):
        ''' reads the stored metadata from the metadata.json file inside cache '''
        if os.path.isfile(os.path.join(self.cache_path, 'metadata.json')):
            with open(os.path.join(self.cache_path, 'metadata.json'), 'r') as file:
                self.metadata = json.load(file)


    def writeMetadata(self):
        with open(os.path.join(self.cache_path, 'metadata.json'), mode='w') as file:
            json.dump(self.metadata, file, indent=3)


    def walkLibrary(self):
        ''' 
            walks the library to find all books. if one/more books do not appear in the 
            metadata.json inside the cache folder, it opens the book and extracts the data.
        '''
        items = os.listdir(self.library_path)
        for item in items:
            if os.path.isfile(os.path.join(self.library_path, item)) and item.endswith('.rmb'):
                self.books_in_library.append(item)

        for book in self.books_in_library:
            if book[:-4] not in self.metadata.keys():
                try:
                    with open(os.path.join(self.library_path, book), 'rb') as file:
                        zip_data = file.read()
                    zip_memory = io.BytesIO(zip_data)

                    with zipfile.ZipFile(zip_memory, 'r') as zip_ref:
                        with zip_ref.open('setup.ini') as file:
                            setup_contents = file.read().decode('utf-8')

                    config = ConfigObj(setup_contents.splitlines())
                    meatdata = config.get('metadata', {})
                    self.metadata[book[:-4]] = self.default_metadata.copy()
                    self.metadata[book[:-4]].update(meatdata)
                    print(self.default_metadata)
                except Exception as e:
                    print(f'error while retriving metadata: {e}')
        self.writeMetadata()


    def walkCoverCache(self) -> None:
        ''' walks the cache to find all covers '''
        items = os.listdir(self.cache_path)
        for item in items:
            if os.path.isfile(os.path.join(self.cache_path, item)) and item.endswith('.png'):
                self.covers_in_cache.append(item)
        
        covers_not_in_chache = []
        for item in self.books_in_library:
            bookname = item[:-4]
            covername = f'cover-{bookname}.png'
            if covername not in self.covers_in_cache:
                self.retrieveCover(item)
                covers_not_in_chache.append(item)


    def retrieveCover(self, book_name:str) -> None:
        ''' extracts the cover from the book '''
        bookname = book_name[:-4]
        try:
            with open(os.path.join(self.library_path, book_name), 'rb') as file:
                zip_data = file.read()
            zip_memory = io.BytesIO(zip_data)

            with zipfile.ZipFile(zip_memory, 'r') as zip_ref:
                zip_ref.extract('cover.png', self.cache_path)
            os.rename(os.path.join(self.cache_path, 'cover.png'), os.path.join(self.cache_path, f'cover-{bookname}.png'))
            self.covers_in_cache.append(f'cover-{bookname}.png')
        except Exception as e:
            print(f'error while retriving a cover: {e}')


    def getCoversList(self) -> list:
        return self.covers_in_cache
    

    def getBooksAndCoversList(self) -> list:
        books_and_covers = []
        for item in self.books_in_library:
            bookname = item[:-4]
            book_data = self.metadata[bookname]
            book_title = f"{book_data['author-first-name']} {book_data['author-last-name']}: {book_data['title']}"
            if f'cover-{bookname}.png' in self.covers_in_cache:    # failsafe in case an error occured while extracting the cover
                books_and_covers.append((os.path.join(self.cache_path, f'cover-{bookname}.png'), book_title, item))
        return books_and_covers
    

    def getLastReadBookAndCover(self) -> list:
        setup = ConfigObj(os.path.join('explorer', 'setup.ini'))
        last_read_file = setup.get('last-read', None)
        if (last_read_file is not None) and (last_read_file in self.books_in_library):
            bookname = last_read_file[:-4]
            if f'cover-{bookname}.png' in self.covers_in_cache:
                book_data = self.metadata[bookname]
                book_title = f"{book_data['author-first-name']} {book_data['author-last-name']}: {book_data['title']}"
                return [(os.path.join(self.cache_path, f'cover-{last_read_file[:-4]}.png'), book_title, last_read_file)]
        return []

if __name__ == '__main__':
    instance = LibraryMaster(r'C:\Users\jovanni\Documents\GitHub\rocky-mountain\library')