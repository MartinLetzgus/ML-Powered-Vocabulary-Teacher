import pickle
import random
import pandas
import time
import warnings
import glob

warnings.filterwarnings("ignore")


class Session:
    def __init__(self, name, vocab_list, logfile):
        self.words = [item[0] for item in vocab_list]
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
            self.df_session["word"] == word, "rounds_last_met1"
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
            self.df_session[f"time_last_met{i}"].apply(lambda x: time.time() - x)
        data = data.to_string(header=False, index=False, index_names=False)
        with open(self.logfile, "a") as f:
            f.write(data + " " + str(res) + "\n")

    def add_words_to_study(self, x):
        actual_len = len(self.words_to_study)
        self.words_to_study = self.words[: actual_len + x]
        return self.words_to_study

    def save(self):
        pickle.dump(self, open(f"../session/{self.name}.pse", "wb"))


def word_to_pair(vocab_list, word):
    return [pair for pair in vocab_list if pair[0] == word][0]


def check_vocab_list(vocab_list):
    assert isinstance(vocab_list, list)
    for item in vocab_list:
        assert isinstance(item, tuple)
        assert isinstance(item[0], str)
        assert isinstance(item[1], list)
        assert len(item[1]) != 0
        for word in item[1]:
            assert isinstance(word, str)


def ask_for_translation(word):
    answer = str(input(f"\n{word} -> "))
    return answer.lower().strip()


def add_words_menu():
    answer = int(input("Number of new words to add : "))
    return answer


def menu():
    print(
        "\nThis is the menu. To come back to the menu during the practice, "
        "just write digits in place of your answer."
    )
    print("Some options are available :")
    print("  practice    ->    start the practice !")
    print("  info        ->    give info about the current session")
    print("  add_words   ->    allow to add more words to your training")
    print("  quit        ->    exit the lesson")
    answer = str(input("\n  -> "))
    return answer.lower().strip()


def pick_a_session():
    session_dict = {"new": "new"}
    print("Choose a session :")
    for session_file in glob.glob("../session/*.pse"):
        session_name = session_file[11:-4].lower()
        session_dict.update({session_name: session_file})
        print(f"  -{session_name}")
    print("  -new")
    answer = str(input("-> ")).lower().strip()
    return session_dict.get(answer)


def ask_session_name():
    answer = str(input("Session name -> ")).strip()
    return answer


if __name__ == "__main__":
    vocab_list = pickle.load(open("../vocab_list/german_english_500.pvl", "rb"))
    check_vocab_list(vocab_list)

    # session_name = "german_english_500"
    # session = Session(vocab_list, "../logs/german_english_500.log")
    # session = pickle.load(open(f"../session/{session_name}.pse", "rb"))

    print(
        "The vocab and the session have been loaded without incidents. Let's start !\n"
    )
    session_file = None
    while not session_file:
        session_file = pick_a_session()
        if not session_file:
            print("Please choose a valid options")
        elif session_file != "new":
            session = pickle.load(open(session_file, "rb"))
            assert isinstance(session, Session)
        else:
            session_name = ask_session_name()
            session = Session(session_name, vocab_list, f"../logs/{session_name}.log")

    while True:
        choice = menu()
        if choice == "practice":
            pair = word_to_pair(
                vocab_list, random.choice(session.words_to_study)
            )  # Not clean
            word, good_answers = pair
            good_answers = [item.lower() for item in good_answers]
            answer = ask_for_translation(word)
            while not answer or answer[0] not in "0123456789":
                if answer in good_answers:
                    print(f"Well played ! The good answers were : {good_answers}")
                else:
                    print(f"Oh no you failed ! The good answers were : {good_answers}")

                res = answer in good_answers
                session.write_to_logfile(word, res)
                session.update(word, res)
                session.save()

                pair = word_to_pair(
                    vocab_list, random.choice(session.words_to_study)
                )  # Not clean
                word, good_answers = pair
                good_answers = [item.lower() for item in good_answers]
                answer = ask_for_translation(word)

        elif choice == "info":
            print(
                f"\nOn this session {session.nb_rounds} rounds have been played and "
                f"you are training on {len(session.words_to_study)} words right now !"
            )
        elif choice == "add_words":
            answer = add_words_menu()
            session.add_words_to_study(answer)
            print(
                f"\n{answer} words have well been added to the set of words you train on !"
            )
        elif choice == "quit":
            break
        else:
            print("\nPlease choose a valid option")
