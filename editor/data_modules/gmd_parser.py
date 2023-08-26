from configobj import ConfigObj
import os

class GMDParser():
    def __init__(self):
        config = ConfigObj(os.path.join('editor', 'setup_files', 'styles.ini'))
        body_styles = config['body']
        tags_styles = config['tags']
        stag_styles = config['speech']

        #:: : build body stylesheet
        self.stylesheet = f'''style="font-family:{body_styles['font-family']}; font-size:{body_styles['font-size']}" align="{body_styles['align']}"'''
        self.break_stylesheet = f'''style="font-family:{body_styles['font-family']}; font-size:{int(body_styles['font-size'][:2])+5}px; font-weight:bold" align="center"'''

        #::: build tags stylesheet dict
        self.tags_dict = {}
        for tag in tags_styles:
            html_tag_style = 'style="'
            for prop in tags_styles[tag]:
                html_tag_style += f'{prop}:{tags_styles[tag][prop]}; '
            html_tag_style = html_tag_style[:-1]+'"'
            if tag == 'ch':
                html_start_tag = f'<span {html_tag_style} align="center">'
            else:
                html_start_tag = f'<span {html_tag_style}>'
            
            html_end_tag = '</span>'

            self.tags_dict[tag] = {
                'start_tag': f'&lt;{tag}&gt;',
                'end_tag': f'&lt;/{tag}&gt;',
                'html_start_tag': html_start_tag,
                'html_end_tag': html_end_tag
            }

        #::: build speech stylesheet dict
        self.stags_dict = {}
        for stag in stag_styles:
            html_tag_style = 'style="'
            for prop in stag_styles[stag]:
                html_tag_style += f'{prop}:{stag_styles[stag][prop]}; '
            html_tag_style = html_tag_style[:-1]+'"'
            html_start_tag = f'<span {html_tag_style}>'
            html_end_tag = '</span>'

            self.stags_dict[stag] = {
                'start_tag': f'[{stag}|',
                'end_tag': ']',
                'html_start_tag': html_start_tag,
                'html_end_tag': html_end_tag
            }


    def parseDocument(self, body_text: str|None = None) -> str:
        if body_text is None:
            with open('body.txt', encoding = 'utf-8', mode = 'r') as file:
                body_text = file.read()

        for item in [('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;')]:     # replace HTML special characters with escape seq
            body_text = body_text.replace(item[0], item[1])

        #::: add html for tags
        for _ in self.tags_dict:
            body_text = body_text.replace(self.tags_dict[_]['start_tag'], self.tags_dict[_]['html_start_tag']+self.tags_dict[_]['start_tag'])
            body_text = body_text.replace(self.tags_dict[_]['end_tag'], self.tags_dict[_]['end_tag']+self.tags_dict[_]['html_end_tag'])

        #::: add html for stags
        for _ in self.stags_dict:
            body_text = body_text.replace(self.stags_dict[_]['start_tag'], self.stags_dict[_]['html_start_tag']+self.stags_dict[_]['start_tag'])
            body_text = body_text.replace(self.stags_dict[_]['end_tag'], self.stags_dict[_]['end_tag']+self.stags_dict[_]['html_end_tag'])

        #::: add the stylesheet to every paragraph
        paragraphs = body_text.split('\n\n')
        for index, para in enumerate(paragraphs):
            para = para.strip()
            if para == '&lt;break&gt;':
                paragraphs[index] = f'<p {self.break_stylesheet}>{para}</h3>'
            else:
                paragraphs[index] = f'<p {self.stylesheet}>'+para+'</p>'
        body_text = '\n\n'.join(paragraphs)

        #::: add the HTML markers to the body
        body_text = f'<html>\n<body>\n{body_text}\n</body>\n</html>'

        return body_text


    def parse_para(self, para:str) -> str:
        for item in [('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;')]:     # replace HTML special characters with escape seq
            para = para.replace(item[0], item[1])

        if '&lt;break&gt;' in para:
            para = f'<p {self.break_stylesheet}>{para}</p>'
            print(para)
            return para

        #::: add html for tags
        for _ in self.tags_dict:
            para = para.replace(self.tags_dict[_]['start_tag'], self.tags_dict[_]['html_start_tag']+self.tags_dict[_]['start_tag'])
            para = para.replace(self.tags_dict[_]['end_tag'], self.tags_dict[_]['end_tag']+self.tags_dict[_]['html_end_tag'])

        #::: add html for stags
        for _ in self.stags_dict:
            para = para.replace(self.stags_dict[_]['start_tag'], self.stags_dict[_]['html_start_tag']+self.stags_dict[_]['start_tag'])
            para = para.replace(self.stags_dict[_]['end_tag'], self.stags_dict[_]['end_tag']+self.stags_dict[_]['html_end_tag'])

        para = f'<p {self.stylesheet}>'+para+'</p>'
        # print(para)
        return para

    def plaintext2gmd(plaintext:str) -> str:
        paragraphs = plaintext.split('\n')

        return '\n\n'.join(paragraphs)


if __name__ == '__main__':
    # parse()
    # print(parse_para('[h|Messages], he said, tossing his shirt on the floor and kicking off his shoes.'))
    pass