import csv
import numpy as np
from sklearn.model_selection import train_test_split
import nltk
from nltk.tokenize import word_tokenize
from random import shuffle
from sklearn.model_selection import KFold
from statistics import mode
import re

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
classifier = nltk.NaiveBayesClassifier.train(training_set)

print("testing")
print("Classifier accuracy percent:", (nltk.classify.accuracy(classifier, testing_set)) * 100)

def sentiment(text):
    feats = find_features(word_tokenize(text))
    v = classifier.classify(feats)
    return mode(v)


print(sentiment("This movie was awesome! The acting was great, plot was wonderful, and there were pythons...so yea!"))
print(sentiment("sorry. Horrible movie, 0/10"))
