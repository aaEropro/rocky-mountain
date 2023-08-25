
for i in range(2, 7):
    path_in = r'C:\Users\jovanniBoss\Desktop\section_'+str(i)+'.txt'
    path_out = r'C:\Users\jovanniBoss\Desktop\split_00'+str(i-1)+'.gmd'

    with open(path_in, encoding='utf-8', mode='r') as file:
        contents = file.read()

    new_contents = ''

    paragraphs = contents.split('\n')
    for para in paragraphs:
        para = para.strip()
        if para != '':
            for item in [('“', '[h|'), ('”', ']')]:
                para = para.replace(item[0], item[1])
            new_contents += '\n\n' + para

    with open(path_out, encoding='utf-8', mode='w') as file:
        file.write(new_contents)