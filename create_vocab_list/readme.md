This folder does not contain anything important, it just shows how I created the vocabulary list.

I first made a txt file from the list available on this website : http://frequencylists.blogspot.com/2016/05/the-500-most-frequently-used-german.html

Then I transformed it into the form :
[(german_word : [english_trad1, english_trad2]), (german_word : [english_trad1, english_trad2, , english_trad3]), ...]

The german word is a string, the english translations are strings into a list. The final result is stored as a pickle file in the vocab_lis/ folder.