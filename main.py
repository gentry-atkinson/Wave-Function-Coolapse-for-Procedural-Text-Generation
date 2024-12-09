# Author: Gentry Atkinson
# Organization: St. Edwards University
# Date: December 5th, 2024

import requests

import re
from wave_text import WaveText
import nltk
import os

# TODO:
#  - use NLP module to scrub punctuation and separate words correctly
#  - support training on multiple texts

text_list = os.listdir('text')
text_list.remove('sources.txt')

nltk.download('punkt_tab')

if __name__ == '__main__':
    book_text = open(os.path.join('text', text_list[0])).read()

    book_text = book_text.replace('\r', '')
    book_text = book_text.replace('\n', '')
    book_text = book_text.replace('*', '')
    sentences = nltk.tokenize.sent_tokenize(book_text)


    wt = WaveText(max_dist=1)
    wt.fit(sentences)
    
    sample_output = wt.generate("all people", str_len=12)
    print(sample_output)