import pickle


class Vocab:
    def __init__(self, name):
        self.name = name
        self.file = f"../vocab_list/{self.name}.pvl"
        self.vocab_list = pickle.load(open(self.file, "rb"))
        self.check_vocab_list()
        # '../vocab_list/german_english_500.pv'

    def check_vocab_list(self):
        assert isinstance(self.vocab_list, list)
        for item in self.vocab_list:
            assert isinstance(item, tuple)
            assert isinstance(item[0], str)
            assert isinstance(item[1], list)
            assert len(item[1]) != 0
            for word in item[1]:
                assert isinstance(word, str)

    def word_to_pair(self, word: str):
        return [pair for pair in self.vocab_list if pair[0] == word][0]
