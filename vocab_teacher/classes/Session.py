from classes.Vocab import Vocab
import pickle
import pandas
import time
import random


class Session:
    def __init__(self, name: str, vocab: Vocab, logfile: str):
        self.vocab = vocab.name
        self.words = [item[0] for item in vocab.vocab_list]
        df_session = pandas.DataFrame(
            columns=[
                "word",
                "rounds_last_met1",
                "words_last_met1",
                "time_last_met1",
                "res_last_met1",
                "rounds_last_met2",
                "words_last_met2",
                "time_last_met2",
                "res_last_met2",
                "rounds_last_met3",
                "words_last_met3",
                "time_last_met3",
                "res_last_met3",
                "rounds_last_met4",
                "words_last_met4",
                "time_last_met4",
                "res_last_met4",
                "rounds_last_met5",
                "words_last_met5",
                "time_last_met5",
                "res_last_met5",
            ]
        )
        df_session["word"] = self.words
        for col in [
            "rounds_last_met1",
            "words_last_met1",
            "rounds_last_met2",
            "words_last_met2",
            "rounds_last_met3",
            "words_last_met3",
            "rounds_last_met4",
            "words_last_met4",
            "rounds_last_met5",
            "words_last_met5",
        ]:
            df_session[col] = [100] * len(self.words)
        for col in [
            "time_last_met1",
            "time_last_met2",
            "time_last_met3",
            "time_last_met4",
            "time_last_met5",
        ]:
            df_session[col] = [time.time()] * len(self.words)
        for col in [
            "res_last_met1",
            "res_last_met2",
            "res_last_met3",
            "res_last_met4",
            "res_last_met5",
        ]:
            df_session[col] = [False] * len(self.words)

        self.name = name
        self.df_session = df_session
        self.logfile = logfile
        self.nb_rounds = 0
        self.list_words = []  # TODO - Optimize this and the update of words_last_met
        self.words_to_study = self.words[:10]

    def update(self, word, res):
        assert word in self.df_session["word"].to_list()
        self.nb_rounds += 1
        for i in range(5, 1, -1):
            self.df_session.loc[
                self.df_session["word"] == word, f"rounds_last_met{i}"
            ] = self.df_session.loc[
                self.df_session["word"] == word, f"rounds_last_met{i-1}"
            ]
            self.df_session.loc[
                self.df_session["word"] == word, f"time_last_met{i}"
            ] = self.df_session.loc[
                self.df_session["word"] == word, f"time_last_met{i-1}"
            ]
            self.df_session.loc[
                self.df_session["word"] == word, f"res_last_met{i}"
            ] = self.df_session.loc[
                self.df_session["word"] == word, f"res_last_met{i-1}"
            ]
        self.df_session.loc[self.df_session["word"] == word, "rounds_last_met1"] = 0
        self.df_session.loc[
            self.df_session["word"] == word, "time_last_met1"
        ] = time.time()
        self.df_session.loc[self.df_session["word"] == word, "res_last_met1"] = res
        for i in range(1, 6):  # We could update only the words_to_study
            self.df_session[f"rounds_last_met{i}"] += 1
        for i in range(1, 6):  # We could update only the words_to_study
            list_words_last_met = []
            for row in self.df_session.iterrows():
                if row[1][f"rounds_last_met{i}"] < 100:
                    list_words_last_met.append(
                        len(set(self.list_words[row[1][f"rounds_last_met{i}"] + 1 :]))
                    )
                else:
                    list_words_last_met.append(100)
            self.df_session[f"words_last_met{i}"] = list_words_last_met

        self.list_words.append(word)

    def write_to_logfile(self, word, res):
        data = self.df_session.loc[self.df_session["word"] == word]
        # We convert absolute time into timediff
        for i in range(1, 6):  # We could update only the words_to_study
            data[f"time_last_met{i}"] = round(time.time() - data[f"time_last_met{i}"])
        data = data.to_string(header=False, index=False, index_names=False)
        with open(self.logfile, "a") as f:
            f.write(data + " " + str(res) + "\n")

    def add_words_to_study(self, x):
        actual_len = len(self.words_to_study)
        self.words_to_study = self.words[: actual_len + x]
        return self.words_to_study

    def get_word(self, vocab: Vocab) -> tuple[str, list[str]]:
        pair = vocab.word_to_pair(random.choice(self.words_to_study))
        word, good_answers = pair
        good_answers = [item.lower() for item in good_answers]
        return word, good_answers

    def save(self):
        pickle.dump(self, open(f"../session/{self.name}.pse", "wb"))
