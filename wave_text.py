# Author: Gentry Atkinson
# Organization: St. Edwards University
# Date: December 5th, 2024

import numpy as np
from random import choices, randint
from nltk.tokenize import word_tokenize

# TODO:
#  - adjacency counting should be directional

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
                return 0
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
            
    def __init__(self):
        self.max_dist = 0
        self.neighbor_count = None
        self.cell_list = None

    def fit(self, sentences: list[str], max_dist=1) -> None:
        """
        Initialize the generator by observing the adjacencies in the provided sentences.
        Parameters:
            max_dist : the maximum separation of compared words
            sentences: list of examples senteces as strings
        """
        assert sentences and len(sentences) > 0, "Generator must be provided training text"
        assert max_dist==1, "Relax. I haven't implemented that yet. Max dist must be 1"

        # Setup
        num_uniques, word_set = self._count_uniques(sentences)
        p_of_neighbors = [{word: dict() for word in word_set} for _ in range(max_dist)]
        num_sentences = len(sentences)

        # Count Adjacencies
        for sentence in sentences:
            #sentence_list = sentence.split(' ')
            sentence_list = word_tokenize(sentence)
            for i, word_one in enumerate(sentence_list):
                for word_two in sentence_list[i+1:]:
                    p_of_neighbors[0][word_one][word_two] = p_of_neighbors[0][word_one].get(word_two, 0) + 1
                    p_of_neighbors[0][word_two][word_one] = p_of_neighbors[0][word_two].get(word_one, 0) + 1

        # Divide adjacency count by total 
        for word_one in p_of_neighbors[0]:
            for word_two in p_of_neighbors[0][word_one]:
                p_of_neighbors[0][word_one][word_two] /= num_sentences

        # If everything worked, store adjacencies
        self.neighbor_count = p_of_neighbors.copy()
        self.max_dist = max_dist


    def generate(self, prompt=None, str_len=12) -> str:
        """
        Generate a new sentece using the trained adjacencies.
        """
        assert self.neighbor_count, "Generator must fit before generation. Use WaveText.fit(...)"
        #prompt_list =  prompt.split(' ')
        prompt_list = word_tokenize(prompt)
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
        
        return ' '.join([cell.get_word() for cell in self.cell_list[1:-1]])

    def _propogate(self, cell_idx: int):
        assert self.cell_list[cell_idx].collapsed, "Propogate called for uncolapsed cell"
        cell = self.cell_list[cell_idx]
        this_word = cell.get_word()
        for i in range(1, self.max_dist+1):
            # Lower Neighbor
            if cell_idx - i > 0 and not self.cell_list[cell_idx - i].collapsed:
                for word in self.neighbor_count[i-1][this_word]:
                    self.cell_list[cell_idx - i].update(word, self.neighbor_count[i-1][this_word][word])

            # Upper Neighbor
            if cell_idx + i < len(self.cell_list) and not self.cell_list[cell_idx + i].collapsed:
                for word in self.neighbor_count[i-1][this_word]:
                    self.cell_list[cell_idx + i].update(word, self.neighbor_count[i-1][this_word][word])

    
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
        word_set = set(['*START*', '*END*'])
        for sentence in sentences:
            #for word in sentence.split(' '):
            for word in word_tokenize(sentence):
                word_set.add(word)
        return len(word_set), word_set
    
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
        