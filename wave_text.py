# Author: Gentry Atkinson
# Organization: St. Edwards University
# Date: December 5th, 2024

import numpy as np
from random import choices, randint
from nltk.tokenize import word_tokenize
import re

# TODO:
#  - adjacency counting should be directional
#  - New neighbor_count structure
#   {[distance][word 1][word2] : probability}
# e.g. {[1][dog][cat] : the likelihood that cat is immediately after dog}
# e.g. {[-1][dog][cat] : the likelihood that cat is immediately before dog}

def split_sentence_to_words(s: str) -> list[str]:
    tokens = word_tokenize(s)
    tokens = [t for t in tokens if t.isalnum()]
    tokens = [re.sub(r'[^\w\s]', '', t) for t in tokens if re.sub(r'[^\w\s]', '', t)]
    tokens = [t.lower() for t in tokens]
    return tokens

class WaveText:

    class Cell:
        def __init__(self, word=None):
            self.word = word
            if word:
                self.collapsed = True
            else:
                self.collapsed = False
            self.possibles = dict()
        
        def get_max_possible(self) -> float:
            if self.collapsed:
                return 0
            elif len(self.possibles) == 0:
                return -1
            return sorted(list(self.possibles.values()))[-1]
        
        def get_word(self) -> str:
            if self.word != None:
                return self.word
            else:
                return ''
            
        def collapse(self) -> None:
            assert not self.collapsed, "Collapse called on already collapsed cell."
            assert len(self.possibles) > 0, "Collapse called on cell with no possibles"
            self.collapsed = True
            self.word = choices(list(self.possibles.keys()), k=1, weights=list(self.possibles.values()))[0]

        def update(self, word: str, p: float) -> None:
            self.possibles[word] = self.possibles.get(word, 0) + p
            
    def __init__(self, max_dist=1):
        """
        Parameters:
            max_dist : the maximum separation of compared words
        """
        self.max_dist = max_dist
        self.neighbor_count = {n:dict() for n in range(-1*max_dist, max_dist+1) if n != 0}
        self.cell_list = None

    def fit(self, sentences: list[str]) -> None:
        """
        Initialize the generator by observing the adjacencies in the provided sentences.
        Parameters:
            
            sentences: list of examples senteces as strings
        """
        assert sentences and len(sentences) > 0, "Generator must be provided training text"
        # print(sentences[100])

        # Setup
        num_uniques, word_set = self._count_uniques(sentences)
        num_sentences = len(sentences)
        for word in word_set:
            for d in self.neighbor_count:
                if word not in self.neighbor_count[d]:
                    self.neighbor_count[d][word] = dict()

        # Count Adjacencies
        for sentence in sentences:
            #sentence_list = sentence.split(' ')
            sentence_list = split_sentence_to_words(sentence)
            for i, word_one in enumerate(sentence_list):
                for word_two in sentence_list[i+1:]:
                    self.neighbor_count[1][word_one][word_two] = self.neighbor_count[1][word_one].get(word_two, 0) + 1
                    self.neighbor_count[-1][word_two][word_one] = self.neighbor_count[-1][word_two].get(word_one, 0) + 1

        # Divide adjacency count by total 
        for d in self.neighbor_count:
            for word_one in self.neighbor_count[d]:
                for word_two in self.neighbor_count[d][word_one]:
                    self.neighbor_count[d][word_one][word_two] /= num_sentences

        # If everything worked, store adjacencies
        #self.neighbor_count = p_of_neighbors.copy()


    def generate(self, prompt=None, str_len=12) -> str:
        """
        Generate a new sentece using the trained adjacencies.
        """
        assert self.neighbor_count, "Generator must fit before generation. Use WaveText.fit(...)"
        #prompt_list =  prompt.split(' ')
        prompt_list = split_sentence_to_words(prompt)
        assert len(prompt_list) < str_len, "Prompt is too long for given string length."

        empty_cells = self._get_padding_cells(str_len-len(prompt_list), len(prompt_list)+1)
        self.cell_list = [WaveText.Cell('*START*')]
        for i, prompt_word in enumerate(prompt_list):
            self.cell_list.extend([WaveText.Cell() for _ in range(empty_cells[i])])
            self.cell_list.extend([WaveText.Cell(prompt_word)])
        self.cell_list.extend([WaveText.Cell() for _ in range(empty_cells[-1])] + [WaveText.Cell('*END*')])

        # Propogate likelihoods from initial cells
        for cell_idx, _ in enumerate(self.cell_list):
            if not self.cell_list[cell_idx].collapsed:
                continue
            self._propogate(cell_idx)
            


        while not all([cell.collapsed for cell in self.cell_list]):
            # print(' '.join([cell.get_word() for cell in self.cell_list]))
            # Pick the lowest entroy cell
            cell_idx = self._min_entropy(self.cell_list)

            # Collapse the chosen cell
            self.cell_list[cell_idx].collapse()

            # Propogate the change
            this_word = self.cell_list[cell_idx].get_word()
            self._propogate(cell_idx)
        
        out_str = ' '.join([cell.get_word() for cell in self.cell_list[1:-1]])
        return out_str[0].upper() + out_str[1:] + '.'

    def _propogate(self, cell_idx: int):
        assert self.cell_list[cell_idx].collapsed, "Propogate called for uncolapsed cell"
        this_word = self.cell_list[cell_idx].get_word()
        for i in self.neighbor_count: # keys: -max_dist up to +max_dist excluding 0
            # Lower Neighbor
            if len(self.cell_list) > cell_idx - i > 0 and not self.cell_list[cell_idx - i].collapsed:
                for word in self.neighbor_count[i][this_word]:
                    self.cell_list[cell_idx - i].update(word, self.neighbor_count[i][this_word][word])

            # Upper Neighbor
            if 0 < cell_idx + i < len(self.cell_list) and not self.cell_list[cell_idx + i].collapsed:
                for word in self.neighbor_count[i][this_word]:
                    self.cell_list[cell_idx + i].update(word, self.neighbor_count[i][this_word][word])

    
    def _get_padding_cells(self, total_sum: int, num_values: int) -> list[int]:
        values = []
        cur_sum = 0
        for _ in range(num_values-1):
            new_num = randint(0, total_sum - cur_sum)
            cur_sum += new_num
            values.append(new_num)
        values.append(total_sum - cur_sum)
        return values

    
    def _min_entropy(self, cell_list: list) -> int:
        """
        Returns the index of the Cell in cell_list with the MOST probable word
        """
        return np.argmax([cell.get_max_possible() for cell in cell_list])

    def _count_uniques(self, sentences: list) -> tuple[int, set]:
        """
        Return the number of numique words in sentences
        """
        word_set = set()
        for sentence in sentences:
            #for word in sentence.split(' '):
            for word in split_sentence_to_words(sentence):
                word_set.add(word)
        return len(word_set), ['*START*'] + [word.lower() for word in word_set] + ['*END*']
    
    def freeze(self, path="") -> None:
        """
        Writes learned adjacencies to disk.
        """
        pass

    def load(self, path: str) -> None:
        """
        Read the stored adjacency dict
        """
        pass
        