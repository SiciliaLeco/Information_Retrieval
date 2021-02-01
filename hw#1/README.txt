This is the README file for E0675841's submission

== Python Version ==

I'm (We're) using Python Version <3.7.4> for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

The task of hw1 is generally divided into two parts:
1. train a LM from the given `input.train.txt`
2. test the given strings to evaluate the correctness

About training models, as we are using simple 4-gram models, I first create a
class "lang_Model", containing three dictionary that stores knowledge of training data.
the format is like:
mlydict = {"naka":1, "akan":2, ...}

About testing models, I created a function called `calc_Prob()` to calculate every probability
for 4gram, formula is: P = (c(4gram) + 1) / (V + cW), cW is variety of all words. This applies to
Add-1 smoothing method.

Noticed there are sentences labelling "other", I'm inspired by [1]'s work, which first calculate
how many 4grams in the test strings don't belong to LM, then divided by len(string), if that
value exceeds the threshold, the string is considered to be labeled "other".

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

build_test_LM.py
essay.txt
README.txt

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, E0675841, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, E0675841, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

the method of operating alien texts is inspired by:
[1] https://github.com/NavePnow/CS3245-Information-Retrieval-NUS/blob/master/HW_%231/build_test_LM.py

general concept:
[2] https://nlp.stanford.edu/IR-book/html/htmledition/language-models-for-information-retrieval-1.html