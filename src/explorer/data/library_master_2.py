import os
import zipfile
from configobj import ConfigObj
from src.settings.data.settings_master import SettingsMasterStn
import zlib



class LibraryMaster:

    default_metadata = {
        "author-first-name": "",
        "author-last-name": "",

        "univers": "",
        "series": "",
        "volume": "",
        "title": "",

        "isbn-e": ""
    }

    def __init__(self, library_path):
        self.metadata = {}
        self.books_in_library = []
        self.library_path = library_path
        self.cache_path = os.path.join(self.library_path, 'cache')
        os.makedirs(self.cache_path, exist_ok=True)    # make sure that the lib path and the cache path lead to existing directories

        self.makeCache()

################################## CACHING ########################################################
    def makeCache(self):
        ''' 
            walks the library loads the covers to cache.
        '''
        items = os.listdir(self.library_path)
        for item in items:
            if os.path.isfile(os.path.join(self.library_path, item)) and item.endswith('.rmb'):
                self.books_in_library.append(item)
                self.checkCachedCover(item)
                self.cacheMetadata(item)


    def checkCachedCover(self, book:str):
        ''' checks if the cover inside the specific .rmb file exists in cache and is identical. '''
        with zipfile.ZipFile(os.path.join(self.library_path, book), 'r') as archive:
            cover_in_archive_crc = archive.getinfo('cover.png').CRC
        
        book_name = book[:-4]
        cover_in_cache_name = f'cover-{book_name}.png'
        if not os.path.isfile(os.path.join(self.cache_path, cover_in_cache_name)):
            self.cacheCover(book, book_name)
            return

        with open(os.path.join(self.cache_path, cover_in_cache_name), 'rb') as png:
            cover_in_cache_crc = zlib.crc32(png.read()) & 0xffffffff    # ensure it's a positive value
        if cover_in_archive_crc != cover_in_cache_crc:
            os.remove(os.path.join(self.cache_path, cover_in_cache_name))
            self.cacheCover(book, book_name)
    

    def cacheCover(self, book:str, book_name:str):
        ''' copy the cover to cache. '''
        with zipfile.ZipFile(os.path.join(self.library_path, book), 'r') as archive:
            archive.extract('cover.png', self.cache_path)
        os.rename(os.path.join(self.cache_path, 'cover.png'), os.path.join(self.cache_path, f'cover-{book_name}.png'))


    def cacheMetadata(self, book:str) -> None:
        ''' adds the metadata of the book to the class metadata dict. '''
        with zipfile.ZipFile(os.path.join(self.library_path, book), 'r') as archive:
            metadata_ini = archive.read('setup.ini').decode().splitlines()
        config = ConfigObj(metadata_ini)
        metadata = config.get('metadata', {})
        self.metadata[book[:-4]] = metadata


################################## COVERS DATA ####################################################
    def getCoversData(self) -> list:
        '''
            returns a list of tuples containing tha path to the cover, the name of the book and the title of the .rmb file.
                ex: [('Desktop\lib\cache\cover-polity-agent.png', 'Neal Asher: Polity Agent', 'polity-agent.rnb')]
        '''
        books_and_covers = []
        for book in self.books_in_library:
            book_name = book[:-4]
            book_metadata = self.metadata[book_name]
            book_title = f"{book_metadata['author-first-name']} {book_metadata['author-last-name']}: {book_metadata['title']}"
            books_and_covers.append((os.path.join(self.cache_path, f'cover-{book_name}.png'), book_title, book))

        return books_and_covers

    ##############################################################################
    def getBookTitle(self, bookname):
        return self.metadata.get(bookname, self.default_metadata)['title']
    

    def getBookAuthor(self, bookname):
        return (self.metadata.get(bookname, self.default_metadata)['author-first-name'], self.metadata.get(bookname, self.default_metadata)['author-last-name'])
    

    def getBookCover(self, bookname):
        book_name = bookname[:-4]
        cover = f'cover-{book_name}.png'
        return cover



# if __name__ == '__main__':
    # instance = LibraryMaster()
    # print(instance.getCoversData())