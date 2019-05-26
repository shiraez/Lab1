import csv
import numpy as np
from nltk import SklearnClassifier
from sklearn.model_selection import train_test_split
import nltk
from nltk.tokenize import word_tokenize
from random import shuffle
from sklearn.model_selection import KFold
from statistics import mode
import re
from sklearn.cross_validation import KFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from nltk.classify import ClassifierI
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC, LinearSVC
from nltk.metrics.scores import (precision, recall)
from nltk import collections


documents = []
with open("data.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for record in csv_reader:
        ap = (' '.join(re.sub("(@[A-Za-z0-9]+)|(\w+:\/\/\S+)", " ", record[1]).split()))
        ap = word_tokenize(ap)
        documents.append((ap, record[0]))

shuffle(documents)

all_words = []
for tweet in documents:
    for w in tweet[0]:
        all_words.append(w.lower())

all_words = nltk.FreqDist(all_words)
print("getting features")
word_features = list(all_words.keys())[:1000]
print(word_features)


def find_features(tweet):
    words = set(tweet)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features


print("setting features per tweet")
feature_sets = np.array([[find_features(tweet), category] for (tweet, category) in documents])

data = feature_sets[:, 0]
target = feature_sets[:, 1]

testing_set = feature_sets[5000:]
training_set = feature_sets[:5000]

print("training")
X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=0.1, random_state=0)

print("testing")


cv = KFold(len(training_set), n_folds=k, shuffle=False, random_state=None)
accur = []
i = 0
for traincv, testcv in cv:
    testing_this_round = training_set[testcv[0]:testcv[len(testcv) - 1]]
    LinearSVC_classifier = SklearnClassifier(LinearSVC())
    classifier = LinearSVC_classifier.train(training_set[traincv[0]:traincv[len(traincv)-1]])
    accur.insert(i,nltk.classify.util.accuracy(classifier, testing_this_round))
    print('accuracy:',accur[i])
    i = i+1
    refsets = collections.defaultdict(set)
    testsets = collections.defaultdict(set)

    for j, (feats, label) in enumerate(testing_this_round):
        refsets[label].add(j)
        observed = classifier.classify(feats)
        testsets[observed].add(j)

    print('Precision:', precision(refsets['1'], testsets['1']))
    print('Recall:', recall(refsets['1'], testsets['1']))
    print('Precision neg:', precision(refsets['0'], testsets['0']))
    print('Recall neg:', recall(refsets['0'], testsets['0']))

print('LinearSVC_classifier average accuracy:',sum(accur) / len(accur) )


def sentiment(text):
    feats = find_features(word_tokenize(text))
    return classifier.classify(feats)
    # votes = []
    # votes.append(v)
    # return mode(votes)


print(sentiment("This movie was awesome! The acting was great, plot was wonderful, and there were pythons...so yea!"))
print(sentiment("sorry. Horrible movie, 0/10"))
