from nltk.corpus import stopwords
import nltk
import random
from nltk.corpus import movie_reviews
from nltk.classify import ClassifierI
from statistics import mode
import pickle
import re
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB,BernoulliNB
from sklearn.linear_model import LogisticRegression,SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
import csv
# documents = [(list(movie_reviews.words(fileid)), category)
#              for category in movie_reviews.categories()
#              for fileid in movie_reviews.fileids(category)]
from sphinx.util import requests

documents = []
set_word = {}
with open("data.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for record in csv_reader:
        ap = (' '.join(re.sub("(@[A-Za-z0-9]+)|(\w+:\/\/\S+)", " ", record[1]).split())).split()
        documents.append((ap, record[0]))


# random.shuffle(documents)

all_words = []

for tweet in documents:
    for w in tweet[0]:
        all_words.append(w.lower())

all_words = nltk.FreqDist(all_words)

word_features = list(all_words.keys())[:1000]

stop_words = set(stopwords.words('english'))
word_features = [w for w in all_words.keys() if not w in stop_words][:1000]



def hashtag_words():
    words = []
    spilthash = re.compile(r"#(\w+)")
    with open("data.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for record in csv_reader:
            words.append(spilthash.findall(record[1]))
    return list(words)

# word_features = hashtag_words()

def find_features(document):
    words = set(document)
    features = {}
    for w in word_features:
        features[w] = (w in words)

    return features


# print((find_features(movie_reviews.words(documents))))
featuresets = [(find_features(rev), category) for (rev, category) in documents]


testing_set = featuresets[900:]
training_set = featuresets[:900]

classifier = nltk.NaiveBayesClassifier.train(training_set)
# classifier_f = open("naivebayes.pickle", "rb")
# classifier = pickle.load(classifier_f)
# classifier_f.close()
# classifier.pr

#
# print("Classifier accuracy percent:",(nltk.classify.accuracy(classifier, testing_set))*100)
#
# print("Classifier accuracy percent:",(nltk.classify.accuracy(classifier, testing_set))*100)

class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def classify(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)
        return mode(votes)

    def confidence(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)

        choice_votes = votes.count(mode(votes))
        conf = choice_votes / len(votes)
        return conf

# classifier.show_most_informative_features(15)
# save_classifier = open("naivebayes.pickle","wb")
# pickle.dump(classifier, save_classifier)
# save_classifier.close()

# MNB_classifier = SklearnClassifier(MultinomialNB())
# MNB_classifier.train(training_set)
# print("MultinomialNB accuracy percent:",nltk.classify.accuracy(MNB_classifier, testing_set))
#
# classifier_f = open("MNB_classifier.pickle", "wb")
# classifier = pickle.dump(MNB_classifier, classifier_f)
# classifier_f.close()
#
# BNB_classifier = SklearnClassifier(BernoulliNB())
# BNB_classifier.train(training_set)
# print("BernoulliNB accuracy percent:",nltk.classify.accuracy(BNB_classifier, testing_set))
#
# classifier_f = open("BNB_classifier.pickle", "wb")
# classifier = pickle.dump(BernoulliNB, classifier_f)
# classifier_f.close()
#
# print("Original Naive Bayes Algo accuracy percent:", (nltk.classify.accuracy(classifier, testing_set))*100)
# classifier.show_most_informative_features(15)
#
# MNB_classifier = SklearnClassifier(MultinomialNB())
# MNB_classifier.train(training_set)
# print("MNB_classifier accuracy percent:", (nltk.classify.accuracy(MNB_classifier, testing_set))*100)
#
#
LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
LogisticRegression_classifier.train(training_set)
print("LogisticRegression_classifier accuracy percent:", (nltk.classify.accuracy(LogisticRegression_classifier, testing_set))*100)


classifier_f = open("LogisticRegression.pickle", "rb")
LogisticRegression_classifier = pickle.load(classifier_f)
classifier_f.close()

#
# SVC_classifier = SklearnClassifier(SVC())
# SVC_classifier.train(training_set)
# print("SVC_classifier accuracy percent:", (nltk.classify.accuracy(SVC_classifier, testing_set))*100)
#
# LinearSVC_classifier = SklearnClassifier(LinearSVC())
# LinearSVC_classifier.train(training_set)
# print("LinearSVC_classifier accuracy percent:", (nltk.classify.accuracy(LinearSVC_classifier, testing_set))*100)
#
# NuSVC_classifier = SklearnClassifier(NuSVC())
# NuSVC_classifier.train(training_set)
# print("NuSVC_classifier accuracy percent:", (nltk.classify.accuracy(NuSVC_classifier, testing_set))*100)

voted_classifier = VoteClassifier(
                                  classifier)

# voted_classifier = classifier




def sentiment(text):
    feats = find_features(text)
    return voted_classifier.classify(feats),voted_classifier.confidence(feats)

print(sentiment("This movie was awesome! The acting was great, plot was wonderful, and there were pythons...so yea!"))
print(sentiment("sorry. Horrible movie, 0/10"))
