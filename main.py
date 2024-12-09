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

def split_into_sentences(paragraph):
    # https://medium.com/@ravindul97/sentence-splitting-in-nlp-2948c90de4a2
    # Regular expression pattern
    sentence_endings = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s'
    sentences = re.split(sentence_endings, paragraph)    
    return sentences


text_list = os.listdir('text')
text_list.remove('sources.txt')

nltk.download('punkt_tab')

if __name__ == '__main__':
    print(text_list)
    book_text = open(os.path.join('text', text_list[0])).read()

    book_text = book_text.replace('\r', '')
    book_text = book_text.replace('\n', '')
    book_text = book_text.replace('*', '')
    sentences = nltk.tokenize.sent_tokenize(book_text)


    wt = WaveText()
    wt.fit(sentences)
    
    sample_output = wt.generate("all people", str_len=12)
    print(sample_output)