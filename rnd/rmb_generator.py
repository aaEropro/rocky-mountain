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

global names_list
names_list = []

def getItalicClasses(epub_book):
    italic_classes = set()

    for item in epub_book.get_items():
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


def getBoldClasses(epub_book):
    bold_classes = set()

    for item in epub_book.get_items():
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


def getBoldItalicClasses(epub_book):
    bold_italic_classes = set()

    for item in epub_book.get_items():
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


def extract_text_from_epub(epub_path, output_dir):
    book = epub.read_epub(epub_path)
    italic_classes = getItalicClasses(book)
    bold_classes = getBoldClasses(book)
    bold_italic_classes = getBoldItalicClasses(book)

    for item in bold_italic_classes:    # make sure there are not bold-italic duplicates
        italic_classes = [x for x in italic_classes if x != item]
        bold_classes = [x for x in bold_classes if x != item]

    for idx, item in enumerate(book.get_items()):
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')

            # Handle HTML tags that traditionally indicate italic text
            for tag in soup.find_all(['i', 'em', 'cite']):
                tag.replace_with(NavigableString(' <e>' + ' '.join(tag.get_text().split()) + '</e> '))

            # Find tags with the italic classes
            for class_name in italic_classes:
                for tag in soup.find_all(class_=class_name):
                    tag.replace_with(NavigableString(' <e>' + ' '.join(tag.get_text().split()) + '</e> '))

            # Extract paragraph text, eliminating double spaces and newline characters
            for para in soup.find_all('p'):
                para.string = ' '.join(para.get_text().split())

            text = soup.get_text('\n')

            text = cleanText(text)

            # Save each section to a separate txt file
            name = f'split_{"0"*(3-len(str(idx)))+str(idx)}.gmd'
            global names_list
            names_list.append(name)
            with open(os.path.join(output_dir, name), 'w', encoding='utf-8') as f:
                f.write(text)


def cleanText(text):
    SETS_TO_BE_REPLACED = (
        ('—', ' -- '), ('–', ' -- '), 
        (' "', ' [h|'), ('" ', '] '), ('“', '[h|'), ('”', ']'), 
        (' ‘', ' <a>'), ('’ ', '</a> '), (" '", ' <a>'), ("' ", '</a> '), 
        (' ]', ']'), ('[h| ', '[h|')
    )

    paragraphs = text.split('\n')
    new_paragraphs = []
    for index, para in enumerate(paragraphs):
        para = para.strip()
        if para != '':
            new_paragraphs.append(para)
        # paragraphs[index] = para
    text = '\n\n'.join(new_paragraphs)
    

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
    setup.write()

    global names_list
    names_list = list(*[names_list])
    names_list.sort()
    order = ConfigObj(os.path.join(output, 'order.ini'))

    order['files-order'] = names_list
    order.write()


def main():
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

    extract_text_from_epub(epub_file, directory)
    writeINIFiles(directory)
    sys.exit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main()
    sys.exit(app.exec())