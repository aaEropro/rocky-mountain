import os
import zipfile
from configobj import ConfigObj
from src.settings.data.settings_master import SettingsMasterStn
import zlib



class LibraryMasterStn():
    '''
        a singleton class that manages the library and books.
    '''
    __instance = None
    library_path = None
    cache_path = None
    metadata = {}
    books_in_library = []

    default_metadata = {
        "author-first-name": "",
        "author-last-name": "",

        "univers": "",
        "series": "",
        "volume": "",
        "title": "",

        "isbn-e": ""
    }


    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(LibraryMasterStn, cls).__new__(cls)
            cls.atCreation()
        return cls.__instance
    

    @classmethod
    def atCreation(cls):
        library_path = SettingsMasterStn().getSpecific('library-path')

        cls.library_path = library_path
        cls.cache_path = os.path.join(cls.library_path, 'cache')
        os.makedirs(cls.cache_path, exist_ok=True)    # make sure that the lib path and the cache path lead to existing directories

        cls.makeCache()

################################## CACHING ########################################################
    @classmethod
    def makeCache(cls):
        ''' 
            walks the library loads the covers to cache.
        '''
        items = os.listdir(cls.library_path)
        for item in items:
            if os.path.isfile(os.path.join(cls.library_path, item)) and item.endswith('.rmb'):
                cls.books_in_library.append(item)
                cls.checkCachedCover(item)
                cls.cacheMetadata(item)


    @classmethod
    def checkCachedCover(cls, book:str):
        ''' checks if the cover inside the specific .rmb file exists in cache and is identical. '''
        with zipfile.ZipFile(os.path.join(cls.library_path, book), 'r') as archive:
            cover_in_archive_crc = archive.getinfo('cover.png').CRC
        
        book_name = book[:-4]
        cover_in_cache_name = f'cover-{book_name}.png'
        if not os.path.isfile(os.path.join(cls.cache_path, cover_in_cache_name)):
            cls.cacheCover(book, book_name)
            return

        with open(os.path.join(cls.cache_path, cover_in_cache_name), 'rb') as png:
            cover_in_cache_crc = zlib.crc32(png.read()) & 0xffffffff    # ensure it's a positive value
        if cover_in_archive_crc != cover_in_cache_crc:
            os.remove(os.path.join(cls.cache_path, cover_in_cache_name))
            cls.cacheCover(book, book_name)
    

    @classmethod
    def cacheCover(cls, book:str, book_name:str):
        ''' copy the cover to cache. '''
        with zipfile.ZipFile(os.path.join(cls.library_path, book), 'r') as archive:
            archive.extract('cover.png', cls.cache_path)
        os.rename(os.path.join(cls.cache_path, 'cover.png'), os.path.join(cls.cache_path, f'cover-{book_name}.png'))


    @classmethod
    def cacheMetadata(cls, book:str) -> None:
        ''' adds the metadata of the book to the class metadata dict. '''
        with zipfile.ZipFile(os.path.join(cls.library_path, book), 'r') as archive:
            metadata_ini = archive.read('setup.ini').decode().splitlines()
        config = ConfigObj(metadata_ini)
        metadata = config.get('metadata', {})
        cls.metadata[book[:-4]] = metadata



################################## COVERS DATA ####################################################
    @classmethod
    def getCoversData(cls) -> list:
        '''
            returns a list of tuples containing tha path to the cover, the name of the book and the title of the .rmb file.
                ex: [('Desktop\lib\cache\cover-polity-agent.png', 'Neal Asher: Polity Agent', 'polity-agent.rnb')]
        '''
        books_and_covers = []
        for book in cls.books_in_library:
            book_name = book[:-4]
            book_metadata = cls.metadata[book_name]
            book_title = f"{book_metadata['author-first-name']} {book_metadata['author-last-name']}: {book_metadata['title']}"
            books_and_covers.append((os.path.join(cls.cache_path, f'cover-{book_name}.png'), book_title, book))

        return books_and_covers

    ##############################################################################
    @classmethod
    def getBookTitle(cls, bookname):
        return cls.metadata.get(bookname, cls.default_metadata)['title']
    

    @classmethod
    def getBookAuthor(cls, bookname):
        return (cls.metadata.get(bookname, cls.default_metadata)['author-first-name'], cls.metadata.get(bookname, cls.default_metadata)['author-last-name'])
    
    @classmethod
    def getBookCover(cls, bookname):
        book_name = bookname[:-4]
        cover = f'cover-{book_name}.png'
        return cover



if __name__ == '__main__':
    instance = LibraryMasterStn()
    print(instance.getCoversData())