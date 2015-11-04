from collections import Counter

import numpy as np
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.datasets import load_files
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import confusion_matrix
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

__author__ = 'James'

classifier1 = SGDClassifier(loss='modified_huber',
                            penalty='l2',
                            alpha=1e-3,
                            n_iter=200,
                            random_state=22)

classifier3 = OneVsRestClassifier(classifier1)

text = load_files('../articles_feed_data/', encoding='utf-8', decode_error='ignore')
print(text.target_names)
class_sizes = Counter()

for label in text.target_names:
    for file in text.filenames:
        if label in file:
            class_sizes.update([label])

pipe = Pipeline([('vect', CountVectorizer()),
                 ('tfidf', TfidfTransformer()),
                 ('feat', LinearSVC()),
                 ('clf', classifier3)])

pipe.fit(text.data, text.target)

"""
Save to file
"""
# pickle.dump(pipe, open('pipe.p', 'wb'))

scores = cross_val_score(pipe, text.data, text.target, cv=10)

X_train, X_test, y_train, y_test = train_test_split(text.data, text.target, random_state=0)
y_pred = pipe.fit(X_train, y_train).predict(X_test)
cm = confusion_matrix(y_test, y_pred)
np.set_printoptions(precision=2)
print('Confusion matrix, without normalization')
print(cm)

print(np.mean(scores))



