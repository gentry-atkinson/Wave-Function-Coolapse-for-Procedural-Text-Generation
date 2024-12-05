# Author: Gentry Atkinson
# Organization: St. Edwards University
# Date: December 5th, 2024

import numpy as np

class WaveText:

    class Cell:
        def __init__(self):
            self.word = None
            self.collapsed = False
            self.possibles = dict()
        
        def get_max_possible(self):
            return sorted(list(self.possibles.values()))[-1]

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
                for word_two in sentence_list[i+1]:
                    p_of_neighbors[0][word_one] = p_of_neighbors[0][word_one].get(word_two, 0) + 1
                    p_of_neighbors[0][word_two] = p_of_neighbors[0][word_two].get(word_one, 0) + 1

        # Divide adjacency count by total 
        for word_one in p_of_neighbors[0]:
            for word_two in p_of_neighbors[0]:
                p_of_neighbors[0][word_one][word_two] /= num_sentences

        # If everything worked, store adjacencies
        self.possibles = p_of_neighbors.copy()    


    def generate(self, prompt=None) -> str:
        """
        Generate a new sentece using the trained adjacencies.
        """
        assert self.possibles, "Generator must fit before generation. Use WaveText.fit(...)"

    def _min_entropy(self, cell_list: list) -> int:
        """
        Returns the index of the Cell in cell_list with the MOST probable word
        """
        pass

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
        