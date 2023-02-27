# ML-Powered-Vocabulary-Teacher
The aim of this project is to test a ML approach to learn vocabulary of a foreign language. Provided with a list of words to learn, the ML model will have to choose which word it should ask for translation at every step. To make this choice, it will try to predict which word is the least likely to be know by the user.

## TODO

✔️ Create a first list of vocabulary, in an appropriate and scalable format

✔️ Create a first interface able to show a word, ask for an answer and write the result in a file to create a first dataset to train the model on

- Train a model and create a function able to choose the word the least likely to be guessed

- Automate the retraining of the model along the training