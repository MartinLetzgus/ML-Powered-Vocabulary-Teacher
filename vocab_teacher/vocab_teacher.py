import pickle
import warnings
import glob

from classes.Session import Session
from classes.Vocab import Vocab

warnings.filterwarnings("ignore")


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


def pick_a_vocab():
    vocab_names = {}
    print("Choose a vocabulary to study :")
    list_vocabs = glob.glob("../vocab_list/*.pvl")
    if list_vocabs:
        for vocab_file in list_vocabs:
            vocab_name = vocab_file[14:-4].lower()
            print(f"  -{vocab_name}")
            vocab_names.update({vocab_name: vocab_name})
        answer = str(input("-> ")).lower().strip()
        return vocab_names.get(answer)  # return None if not one of the options
    else:
        raise ValueError("There is no vocab available at : '../vocab_list/*.pvl'")


def ask_session_name():
    answer = str(input("Session name -> ")).strip()
    return answer


def pick_vocab_session() -> tuple[Vocab, Session]:
    session_file = None
    vocab_name = None
    while not session_file:
        session_file = pick_a_session()
        if not session_file:
            print("Please choose a valid options")
        elif session_file != "new":
            session = pickle.load(open(session_file, "rb"))
            assert isinstance(session, Session)
            vocab = Vocab(session.vocab)
        else:
            session_name = ask_session_name()
            while not vocab_name:
                vocab_name = pick_a_vocab()
                if not vocab_name:
                    print("Please choose a valid options")
                else:
                    vocab = Vocab(vocab_name)
                    session = Session(
                        session_name, vocab, f"../logs/{session_name}.log"
                    )
    return vocab, session


if __name__ == "__main__":

    vocab, session = pick_vocab_session()
    print("The vocab and the session have been loaded without incidents.\n")

    while True:
        choice = menu()
        if choice == "practice":  # Not clean
            word, good_answers = session.get_word(vocab)
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

                word, good_answers = session.get_word(vocab)
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
                f"\n{answer} words have been added to the set of words you train on !"
            )
        elif choice == "quit":
            break
        else:
            print("\nPlease choose a valid option")
