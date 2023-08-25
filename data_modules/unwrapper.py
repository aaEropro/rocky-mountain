########################################################
# companions = [ - ' + = _ ]
# 
# base = [ . ; ]
# 
# emotional = [ ? ! … ] or any combination of them
# 
# structural = [ , : ( ) ]
# 
# other = [a b c ...] all ther characters
# 
# structure of a word:
#    - start transmission marker
#    - start property tag
#    - other (the actual word)
#    - end property tag
#    - emotional
#    - end transmission marker
#    - structural
#    - base
# 
#   example: ([h:p|<e>hello<\e>?!]),
# 
# this is what the unwrapper needs to split any given word into
# 
##########################################################

def unwrap(word):
    in_works = word

    stuff_before = ''

    start_transmission_marker = ''
    start_property_tag = ''
    word_content = ''
    end_property_tag = ''
    emmotional_sequence = ''
    end_transmission_marker = ''
    structural_sequence = ''
    base_sequence = ''

    stuff_after = ''

    # unwrap the start transmission
    index = 0
    flag = False
    while index < len(in_works):
        if in_works[index] == '[':
            flag = True
            stuff_before += in_works[:index]
        elif in_works[index] == '|':
            start_transmission_marker += '|'
            # start_transmission_marker_flag = False
            break
        if flag:
            start_transmission_marker += in_works[index]
        index += 1
    if flag:
        in_works = in_works[index+1:]


    # unwrap the start property
    index = 0
    flag = False
    while index < len(in_works):
        if in_works[index] == '<' and in_works[index+2] == '>':
            flag = True
            stuff_before += in_works[:index]
        elif in_works[index] == '>' and in_works[index-2] == '<':
            start_property_tag += '>'
            # flag = False
            break
        if flag:
            start_property_tag += in_works[index]
        index += 1
    if flag:
        in_works = in_works[index+1:]


    # unwrap the word
    index = 0
    flag = False
    while index < len(in_works):
        if in_works[index] in ['…', '.', ';', '?', '!', '<', '>', '[', ']', ',', ':', '(', ')']:
            break
        else:
            word_content += in_works[index]
            flag = True
        index += 1
    if flag:
        in_works = in_works[index:]


    # unwrap end property
    index = 0
    flag = False
    while index < len(in_works):
        if in_works[index] == '<' and in_works[index+1] == '/' and in_works[index+3] == '>':
            flag = True
        elif in_works[index] == '>' and in_works[index-2] == '/' and in_works[index-3] == '<':
            end_property_tag += '>'
            # flag = False
            break
        if flag:
            end_property_tag += in_works[index]
        index += 1
    if flag:
        in_works = in_works[index+1:]


    # unwrap emotional sequence
    index = 0
    flag = False
    while index < len(in_works):
        if in_works[index] in ['?', '!', '…']:
            emmotional_sequence += in_works[index]
            flag = True
        else:
            break
        index += 1
    if flag:
        in_works = in_works[index:]


    # unwrap end transmission
    if len(in_works) > 0 and in_works[0] == ']':
        end_transmission_marker = ']'
        in_works = in_works[1:]


    # unwrap structural sequence
    index = 0
    flag = False
    while index < len(in_works):
        if in_works[index] in [ ',', ':', '(', ')']:
            structural_sequence += in_works[index]
            flag = True
        else:
            break
        index += 1
    if flag:
        in_works = in_works[index:]

    # unwrap base sequence
    index = 0
    flag = False
    while index < len(in_works):
        if in_works[index] in ['.', ';']:
            base_sequence += in_works[index]
            flag = True
        else:
            break
        index += 1
    if flag:
        in_works = in_works[index:]
    
    # unwrap stuff after
    stuff_after = in_works

    # print(in_works)
    # print([stuff_before, start_transmission_marker, start_property_tag, word_content, end_property_tag, emmotional_sequence, end_transmission_marker, structural_sequence, base_sequence, stuff_after])
    return [stuff_before, start_transmission_marker, start_property_tag, word_content, end_property_tag, emmotional_sequence, end_transmission_marker, structural_sequence, base_sequence, stuff_after]


# unwrap('<a>help…</a>].')