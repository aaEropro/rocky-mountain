import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Read the book
with open(r'C:\Users\jovanni\Desktop\test.txt', encoding='utf-8', mode='r') as file:
    text = file.read()

# Tokenize the text
tokens = word_tokenize(text)

# POS tag the tokens
tagged = pos_tag(tokens)

# # Convert words that are not names to lowercase
# lowercased = [word.lower() if tag != 'NNP' else word for word, tag in tagged]

# # Join the words back into a single string
# result = ' '.join(lowercased)
names = ['']
for word, tag in tagged:
    if tag == 'NNP':
        names.append(word)
names = [*set(names)]
result = '\n'.join(names)

# Write the result back to a file
with open(r'C:\Users\jovanni\Desktop\test_lowercase.txt', 'w') as file:
    file.write(result)
