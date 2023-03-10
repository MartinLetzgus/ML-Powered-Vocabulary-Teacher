from classes.Vocab import Vocab
from classes.Model import Model
import pickle
from scipy.special import softmax
import pandas
import time
import numpy


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
        headers = ",".join(self.df_session.columns) + ",res\n"
        with open(self.logfile, "a") as f:
            f.write(headers)
        self.nb_rounds = 0
        self.list_words = []  # TODO - Optimize this and the update of words_last_met
        self.words_to_study = self.words[:10]
        self.model = Model(model_type="RandomForestRegressor")
        self.save()

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
        data["res"] = res
        data = data.to_csv(header=False, index=False, index_label=False).replace(
            "\n", ""
        )
        with open(self.logfile, "a") as f:
            f.write(data)

    def add_words_to_study(self, x) -> list[str]:
        actual_len = len(self.words_to_study)
        self.words_to_study = self.words[: actual_len + x]
        return self.words_to_study

    def get_word_random(self) -> str:
        return numpy.random.choice(self.words_to_study)

    def get_word_ml(self, history_size_to_consider: int = 2) -> str:
        assert history_size_to_consider > 0
        assert history_size_to_consider <= 5
        self.model.train(self.logfile, history_size_to_consider)
        preds = []
        for word in self.words_to_study:
            pred = self.model.score(
                self.df_session.loc[self.df_session["word"] == word],
                history_size_to_consider,
            )[0]
            preds.append(1.0 - pred)
            print(f"{word} : {round(1.0-pred, 2)}")

        if numpy.sum(preds) != 0:
            preds = numpy.array(preds)
            preds = numpy.power(preds, 3)
            return numpy.random.choice(self.words_to_study, p=preds / numpy.sum(preds))
            # return numpy.random.choice(self.words_to_study, p=softmax(preds))
        else:
            return numpy.random.choice(self.words_to_study)

    def save(self) -> str:
        filepath = f"../session/{self.name}.pse"
        pickle.dump(self, open(filepath, "wb"))
        return filepath
