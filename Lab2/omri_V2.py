import csv
import pickle

import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from random import shuffle
from sklearn.model_selection import KFold, cross_val_score
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier

documents = []
with open("data.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for record in csv_reader:
        # ap = (' '.join(re.sub("(@[A-Za-z0-9]+)|(\w+:\/\/\S+)", " ", record[1]).split())).split()
        ap = word_tokenize(record[1])
        documents.append((ap, record[0]))

shuffle(documents)

all_words = []
for tweet in documents:
    for w in tweet[0]:
        all_words.append(w.lower())

all_words = nltk.FreqDist(all_words)
print("getting features")
word_features = list(all_words.keys())[:3000]


def find_features(tweet):
    words = set(tweet)
    features = []
    for w in word_features:
        features.append(w in words)
    return features


def find_features_dict(tweet):
    words = set(tweet)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features


print("setting features per tweet")
feature_sets = np.array([[find_features(tweet), category] for (tweet, category) in documents])

data = feature_sets[:, 0]
target = feature_sets[:, 1]

new_data = []
for r in data:
    new_data.append(np.array(r))

data = np.array(new_data)

# testing_set = feature_sets[5000:]
# training_set = feature_sets[:5000]

print("training")


def get_score(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    return model.score(X_test, y_test)


skf = KFold(n_splits=10)
# model = MultinomialNB()
# scores = []
# for train_index, test_index in skf.split(data):
#     X_train, X_test = data[train_index], data[test_index]
#     y_train, y_test = target[train_index], target[test_index]
#     model.fit(X_train, y_train)
#     scores.append(get_score(RandomForestClassifier(), X_train, X_test, y_train, y_test))

filename = 'finalized_model.sav'


def save_model():
    pickle.dump(model, open(filename, 'wb'))


def load_model():
    return pickle.load(open(filename, 'rb'))


# save_model()
model = load_model()
print(model.predict(
    [find_features(word_tokenize("I hate this movie! I dont know who made something so bad"))]))


# X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=0.1, random_state=0)
# classifier = nltk.NaiveBayesClassifier.train(training_set)

print("testing")
# print("Classifier accuracy percent:", (nltk.classify.accuracy(classifier, testing_set)) * 100)
