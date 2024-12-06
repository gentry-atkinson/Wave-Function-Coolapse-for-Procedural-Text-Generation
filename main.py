# Author: Gentry Atkinson
# Organization: St. Edwards University
# Date: December 5th, 2024

import requests

import re
from wave_text import WaveText

def split_into_sentences(paragraph):
    # https://medium.com/@ravindul97/sentence-splitting-in-nlp-2948c90de4a2
    # Regular expression pattern
    sentence_endings = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s'
    sentences = re.split(sentence_endings, paragraph)    
    return sentences

TEXT_URL = "https://www.gutenberg.org/cache/epub/11/pg11.txt"
TEXT_START = 1491
TEXT_END = 148818

if __name__ == '__main__':
    response = requests.get(TEXT_URL)
    assert response.status_code == 200, "Couldn't read text from provided URL."


    book_text = response.text[TEXT_START: TEXT_END]
    book_text = book_text.replace('\r', '')
    book_text = book_text.replace('\n', '')
    sentences = [sentence.strip() for sentence in split_into_sentences(book_text)]

    wt = WaveText()
    wt.fit(sentences)
    
    sample_output = wt.generate("tea was", str_len=12)
    print(sample_output)