# Author: Gentry Atkinson
# Organization: St. Edwards University
# Date: December 5th, 2024

from wave_text import WaveText

import nltk
import os

# TODO:
#  - support training on multiple texts

text_list = os.listdir('text')
text_list.remove('sources.txt')

try:
    nltk.find('tokenizers/punkt')
except:
    nltk.download('punkt_tab')

if __name__ == '__main__':
    wt = WaveText(max_dist=3)

    for text_idx, text_name in enumerate(text_list):
        book_text = open(os.path.join('text', text_list[text_idx])).read()

        book_text = book_text.replace('\r', '')
        book_text = book_text.replace('\n', '')
        sentences = nltk.tokenize.sent_tokenize(book_text)
        print(f'Fitting to text: {text_name}')
        wt.fit(sentences)
    
    sample_output = wt.generate("all people", str_len=12)
    print(sample_output)