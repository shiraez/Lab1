import re
import csv
from random import shuffle
import nltk
import numpy as np
from flask import Flask, request
from nltk import SklearnClassifier
from nltk.tokenize import word_tokenize
from sklearn.model_selection import KFold
from sklearn.svm import LinearSVC
from nltk.metrics.scores import (precision, recall)
from nltk import collections
import pickle

nltk.download('punkt')
app = Flask(__name__)

pickle_model = "LinearSVC_classifier.pickle"
pickle_word_features = "word_features.pickle"
classifier = None
word_features = []


def calc_model():
    global word_features, classifier
    documents = []
    pos = 0
    neg = 0
    with open("data.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for record in csv_reader:
            ap = (' '.join(re.sub("(@[A-Za-z0-9]+)|(\w+:\/\/\S+)", " ", record[1]).split()))
            ap = word_tokenize(ap)
            documents.append((ap, record[0]))
            if '0' == record[0]:
                neg = neg + 1
            elif '1' == record[0]:
                pos = pos + 1

    print("neg ", neg)
    print("pos ", pos)

    shuffle(documents)

    all_words = []
    for tweet in documents:
        for w in tweet[0]:
            all_words.append(w.lower())

    all_words = nltk.FreqDist(all_words)
    print("getting features")
    word_features = list(all_words.keys())[:1000]

    save_pickle(pickle_word_features, word_features)
    print("saved word features")

    print("setting features per tweet")
    feature_sets = np.array([[find_features(tweet), category] for (tweet, category) in documents])

    data = feature_sets[:, 0]

    k = 10
    cv = KFold(k)
    accur = []
    pos_precision = []
    pos_recall = []
    neg_precision = []
    neg_recall = []
    i = 0
    for train_index, test_index in cv.split(data):
        print("starting split " + str(i + 1))
        training_this_round = feature_sets[train_index]
        testing_this_round = feature_sets[test_index]
        linear_svc_classifier = SklearnClassifier(LinearSVC())
        classifier = linear_svc_classifier.train(training_this_round)
        accur.insert(i, nltk.classify.util.accuracy(classifier, testing_this_round))
        print('accuracy:', accur[i])
        i = i + 1
        refsets = collections.defaultdict(set)
        testsets = collections.defaultdict(set)

        for j, (feats, label) in enumerate(testing_this_round):
            refsets[label].add(j)
            observed = classifier.classify(feats)
            testsets[observed].add(j)

        cv_pos_precision = precision(refsets['1'], testsets['1'])
        cv_pos_recall = recall(refsets['1'], testsets['1'])
        cv_neg_precision = precision(refsets['0'], testsets['0'])
        cv_neg_recall = recall(refsets['0'], testsets['0'])

        print('Precision:', precision(refsets['1'], testsets['1']))
        print('Recall:', recall(refsets['1'], testsets['1']))
        print('Precision neg:', precision(refsets['0'], testsets['0']))
        print('Recall neg:', recall(refsets['0'], testsets['0']))
        pos_precision.append(cv_pos_precision)
        pos_recall.append(cv_pos_recall)
        neg_precision.append(cv_neg_precision)
        neg_recall.append(cv_neg_recall)

    print('LinearSVC_classifier average accuracy:', sum(accur) / len(accur))
    print('precision', (sum(pos_precision) / len(accur) + sum(neg_precision) / len(accur)) / 2)
    print('recall', (sum(pos_recall) / len(accur) + sum(neg_recall) / len(accur)) / 2)

    save_pickle(pickle_model, classifier)


def sentiment(text):
    feats = find_features(word_tokenize(text))
    return classifier.classify(feats)


def find_features(tweet):
    global word_features
    words = set(tweet)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features


def save_pickle(filename, what_to_save):
    file = open(filename, "wb")
    pickle.dump(what_to_save, file)
    file.close()


def load_pickle(filename):
    return pickle.load(open(filename, 'rb'))


@app.route('/', methods=['GET', 'POST'])
def handle_request():
    global word_features, classifier

    path_to_file = request.args.get('path')
    if path_to_file is None:
        return "<h2>path to file is invalid</h2>" \
               "<h3>please use: <a href='http://localhost:5000/'>http://localhost:5000/?path=C:\\example\\file.txt</a></h3>"

    classifier = load_pickle(pickle_model)
    word_features = load_pickle(pickle_word_features)

    new_file_name = "predictions.txt"
    output_text = "Results saved to file: 'predictions.txt' in the working directory<br><br>[0 - negative | 1 - positive]<br><h3><u><b>Results</b></u></h3>"
    with open(path_to_file, 'r', encoding='utf-8') as file:
        with open(new_file_name, 'w', encoding='utf-8') as new_file:
            for line in file:
                prediction = sentiment(line)
                new_file.write(prediction)
                new_file.write("\n")
                color = ""
                if prediction == '1':
                    color = "green"
                else:
                    color = "red"
                output_text += "<div style=\'color:" + color + "'>" + prediction + " | " + line + "</div><br>"

    return output_text


if __name__ == '__main__':
    # calc_model()
    app.run(debug=True)
