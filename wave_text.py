# Author: Gentry Atkinson
# Organization: St. Edwards University
# Date: December 5th, 2024

import numpy as np
from random import choices, randint

class WaveText:

    class Cell:
        def __init__(self, word=None):
            self.word = word
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
            
        def collapse(self):
            assert not self.collapsed, "Collapse called on already collapsed cell."
            assert len(self.possibles) > 0, "Collapse called on cell with no possibles"
            self.collapsed = True
            self.word = choices(list(self.possibles.keys()), 1, weights=list(self.possibles.values))
            
    def __init__(self):
        pass

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
            sentence_list = sentence.split(' ')
            for i, word_one in enumerate(sentence_list):
                for word_two in sentence_list[i+1:]:
                    p_of_neighbors[0][word_one][word_two] = p_of_neighbors[0][word_one].get(word_two, 0) + 1
                    p_of_neighbors[0][word_two][word_one] = p_of_neighbors[0][word_two].get(word_one, 0) + 1

        # Divide adjacency count by total 
        for word_one in p_of_neighbors[0]:
            for word_two in p_of_neighbors[0][word_one]:
                p_of_neighbors[0][word_one][word_two] /= num_sentences

        # If everything worked, store adjacencies
        self.possibles = p_of_neighbors.copy()    


    def generate(self, prompt=None, str_len=12) -> str:
        """
        Generate a new sentece using the trained adjacencies.
        """
        assert self.possibles, "Generator must fit before generation. Use WaveText.fit(...)"
        prompt_list =  prompt.split(' ')
        assert len(prompt_list) < str_len, "Prompt is too long for given string length."

        empty_cells = self._get_padding_cells(len(prompt_list)+1, str_len-len(prompt_list))
        cell_list = [WaveText.Cell('*START*')]
        for i, prompt_word in enumerate(prompt_list):
            cell_list = cell_list + [WaveText.Cell() for _ in range(empty_cells[i])]
            cell_list = cell_list = [WaveText.Cell(prompt_word)]
        cell_list = cell_list + [WaveText.Cell() for _ in range(empty_cells[-1])] + [WaveText.Cell('*END*')]

        # Propogate likelihoods from initial cells

        while not all([cell.collapsed for cell in cell_list]):
            # Pick the lowest entroy cell
            cell_idx = self._min_entropy(cell_list)

            # Collapse the chosen cell
            cell_list[cell_idx].collapse()

            # Add new neighbors to cell list

            # Propogate the change
        
        return ' '.join([cell.get_word() for cell in cell_list])

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
            for word in sentence.split(' '):
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
        