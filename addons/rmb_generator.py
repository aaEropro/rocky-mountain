import os
import ebooklib
from ebooklib import epub
import cssutils
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys
from configobj import ConfigObj

global split_list
split_list = []

class EpubTextExtractor():
    def __init__(self, epub_path:str, output_dir:str, names_list:list):
        self.epub_path = epub_path
        self.output_dir = output_dir
        self.names_list = names_list

        self.book = epub.read_epub(epub_path)
        self.italic_classes = self.getItalicClasses()
        self.bold_classes = self.getBoldClasses()
        self.bold_italic_classes = self.getBoldItalicClasses()

        for item in self.bold_italic_classes:    # make sure there are not bold-italic duplicates
            self.italic_classes = [x for x in self.italic_classes if x != item]
            self.bold_classes = [x for x in self.bold_classes if x != item]

        idx = 0
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')

                # Handle HTML tags that traditionally indicate italic text
                for tag in soup.find_all(['i', 'em', 'cite']):
                    tag.replace_with(NavigableString(' <e>' + ' '.join(tag.get_text().split()) + '</e> '))

                # Find tags with the italic classes
                for class_name in self.italic_classes:
                    for tag in soup.find_all(class_=class_name):
                        tag.replace_with(NavigableString(' <e>' + ' '.join(tag.get_text().split()) + '</e> '))

                # Extract paragraph text, eliminating double spaces and newline characters
                for para in soup.find_all('p'):
                    para.string = ' '.join(para.get_text().split())

                text = soup.get_text('\n')    # extract all visible text

                text = self.goToLower(text)

                text = cleanText(text)

                # Save each section to a separate txt file
                name = f'split_{"0"*(3-len(str(idx)))+str(idx)}.gmd'
                global split_list
                split_list.append(name)
                with open(os.path.join(output_dir, name), 'w', encoding='utf-8') as f:
                    f.write(text)
                idx += 1
            print(split_list)


    def getItalicClasses(self):
        italic_classes = set()

        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_STYLE:
                stylesheet = cssutils.parseString(item.get_content())
                for rule in stylesheet:
                    if rule.type == rule.STYLE_RULE:
                        style = cssutils.parseStyle(rule.style.cssText)
                        if style.getPropertyValue('font-style') == 'italic':
                            selectors = rule.selectorList
                            for selector in selectors:
                                if selector.selectorText.startswith('.'):
                                    italic_classes.add(selector.selectorText[1:])
        return italic_classes


    def getBoldClasses(self):
        bold_classes = set()

        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_STYLE:
                stylesheet = cssutils.parseString(item.get_content())
                for rule in stylesheet:
                    if rule.type == rule.STYLE_RULE:
                        style = cssutils.parseStyle(rule.style.cssText)
                        if style.getPropertyValue('font-weight') == 'bold':
                            selectors = rule.selectorList
                            for selector in selectors:
                                if selector.selectorText.startswith('.'):
                                    bold_classes.add(selector.selectorText[1:])
        return bold_classes


    def getBoldItalicClasses(self):
        bold_italic_classes = set()

        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_STYLE:
                stylesheet = cssutils.parseString(item.get_content())
                for rule in stylesheet:
                    if rule.type == rule.STYLE_RULE:
                        style = cssutils.parseStyle(rule.style.cssText)
                        if style.getPropertyValue('font-style') == 'italic' and style.getPropertyValue('font-weight') == 'bold':
                            selectors = rule.selectorList
                            for selector in selectors:
                                if selector.selectorText.startswith('.'):
                                    bold_italic_classes.add(selector.selectorText[1:])
        return bold_italic_classes


    def goToLower(self, text:str):
        i_variants = ['I', 'Ill', 'Id', 'Im', 'Ive']
        paragraphs = text.split('\n')
        new_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para != '':
                new_para = []
                words = para.split(' ')
                for word in words:
                    if not word.islower():
                        processed = self.cleanName(word)
                        if (processed not in self.names_list) and (processed not in i_variants):
                            new_para.append(word.lower())
                        else:
                            new_para.append(word)
                    else:
                        new_para.append(word)
                para = ' '.join(new_para)
                new_paragraphs.append(para)
        text = '\n'.join(new_paragraphs)
        return text


    def cleanName(self, name:str):
        # print(name)
        puctuation = '''()-[]{}'"\<>/@#$%^&*_~'''
        expression = ';:!,?'
        regular_space = '\u0020'
        other_spaces = ['\u00A0', '\u2002','\u2003','\u2009', '\u200A', '\u200B', '\u2007', '\u2008', '\u2001', '\u2000', '\u202F', '\u205F', '\u3000', '\uFEFF']
        regular_dash = '\u002D'
        other_dashes = ['\u2013', '\u2014', '\u2043', '\u2212', '\u2011', '\u2012']

        double_quotes = ['\u0022', '\u201C', '\u201D', '\u201E', '\u2E42', '\uFF02']
        single_quotes = ['\u0027', '\u2018', '\u2019', '\u201A', '\u2E41','\uFF07']
        for item in ['<e>', '</e>', '.']:
            name = name.replace(item, '')

        for item in puctuation:
            name = name.replace(item, '')

        for item in expression:
            name = name.replace(item, '')

        for item in other_dashes:    # replace all other dashes to standars dash
            name = name.replace(item, '')

        for item in ['\u201D']:    # remove closing double qotation marks
            name = name.replace(item, '')

        for item in ['\u201C', '\u201E']:    # replace opening double quotation marks
            name = name.replace(item, '')

        for item in ['\u0022', '\u2E42', '\uFF02']:    # replace/remove other double quotation marks
            name = name.replace(item, '')

        for item in ['\u2019']:    # remove closing single qotation marks
            name = name.replace(item, '')

        for item in ['\u2018', '\u201A']:    # replace opening single quotation marks
            name = name.replace(item, '')

        for item in ['\u0027', '\u2E41', '\uFF07']:    # replace/remove other single quotation marks
            name = name.replace(item, '')
        # print(name)
        return name


def cleanText(text):
    SETS_TO_BE_REPLACED = (
        ('—', ' -- '), ('–', ' -- '), 
        (' "', ' [h|'), ('" ', '] '), ('“', '[h|'), ('”', ']'), 
        (' ‘', ' <a>'), ('’ ', '</a> '), (" '", ' <a>'), ("' ", '</a> '), 
        (' ]', ']'), ('[h| ', '[h|')
    )
    SINGLE_QUOTES = (
        (' "', ' <a>'), ('" ', '</a> '), ('“', '<a>'), ('”', '</a>'), 
        (" '", ' [h|'), ("' ", '] '), (' ‘', ' [h|'), ('’ ', '] '), ('\n‘', '\n[h|'), ('’\n', ']\n'), 
    )

    DOUBLE_QUOTES = (
        (' "', ' [h|'), ('" ', '] '), ('“', '[h|'), ('”', ']'), 
        (' ‘', ' <a>'), ('’ ', '</a> '), (" '", ' <a>'), ("' ", '</a> '), 
    )

    paragraphs = text.split('\n')
    new_paragraphs = []
    for index, para in enumerate(paragraphs):
        para = para.strip()
        if para != '':
            new_paragraphs.append(para)
        # paragraphs[index] = para
    text = '\n\n'.join(new_paragraphs)

    double_quotes_instances = text.count('"') + text.count('“') + text.count('”')
    single_quotes_instances = text.count("'") + text.count('‘') + text.count('’')

    if single_quotes_instances < double_quotes_instances:
        for item in DOUBLE_QUOTES:
            text = text.replace(item[0], item[1])
    else:
        for item in SINGLE_QUOTES:
            text = text.replace(item[0], item[1])
    

    # MAKE NECESARY REPLACEMENTS
    for item in SETS_TO_BE_REPLACED:
        text = text.replace(item[0], item[1])

    text = text.replace('. . .', '…')
    text = text.replace('...', '…')

    # REPLACE TRANSMISION END
    for item in ['!', '?', '…']:
        text = text.replace(item, item+'.')
    for item in ['!', '?', '…', '.', ',']:
        text = text.replace(item+'<e>', '<e>'+item)
        text = text.replace(item+'</e>', '</e>'+item)
    text = text.replace('.]', '].')
    text = text.replace(',]', '],')
    
    return text


def writeINIFiles(output):
    setup = ConfigObj(os.path.join(output, 'setup.ini'))
    setup['last-read'] = {
        'split': 'split_001.gmd',
        'cursor': '0'
    }
    setup['metadata'] = {
        "author-first-name": "Neal",
        "author-last-name": "Asher",
        "univers": "Polity",
        "series": None,
        "volume": None,
        "title": "Hilldiggers",
        "isbn-e": 1975967830863
    }
    setup.write()

    global split_list
    split_list = list(*[split_list])
    split_list.sort()
    order = ConfigObj(os.path.join(output, 'order.ini'))

    order['files-order'] = split_list
    order.write()


def main(epub_file, directory, names_list):
    inst = EpubTextExtractor(epub_file, directory, names_list)
    writeINIFiles(directory)
    # sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    options = QFileDialog.Options()
    epub_file, _ = QFileDialog.getOpenFileName(None, "Select EPUB File", "", "EPUB Files (*.epub);;All Files (*)", options=options)
    if not epub_file:
        print('epub not selected')
        sys.exit()

    options = QFileDialog.Options()
    directory = QFileDialog.getExistingDirectory(None, "Select Directory", "", options=options)
    if not directory:
        print('directory not selected')
        sys.exit()
    main(epub_file, directory)

    sys.exit(app.exec())