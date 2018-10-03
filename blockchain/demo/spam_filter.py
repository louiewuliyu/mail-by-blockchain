# -*- coding: utf-8 -*-
import os
import numpy as np
from collections import Counter
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import confusion_matrix

import copy
import pandas as pd

#prepare extract object
#training
def make_Dictionary(train_dir):
    emails = [os.path.join(train_dir,f) for f in os.listdir(train_dir)]    
    all_words = []       
    for mail in emails:    
        with open(mail) as m:
            for i,line in enumerate(m):
                if i == 2:
                    words = line.split()
                    all_words += words
    
    dictionary = Counter(all_words)
    
    list_to_remove = list(dictionary.keys())
    for item in list_to_remove:
        if item.isalpha() == False: 
            del dictionary[item]
        elif len(item) == 1:
            del dictionary[item]
    dictionary = dictionary.most_common(3000)
    return dictionary

#email features    
def extract_features(mail_dir, dictionary): 
    files = [os.path.join(mail_dir,fi) for fi in os.listdir(mail_dir)]
    features_matrix = np.zeros((len(files),3000))
    docID = 0;
    for fil in files:
      with open(fil) as fi:
        for i,line in enumerate(fi):
          if i == 2:
            words = line.split()
            for word in words:
              wordID = 0
              for i,d in enumerate(dictionary):
                if d[0] == word:
                  wordID = i
                  features_matrix[docID,wordID] = words.count(word)
        docID = docID + 1     
    return features_matrix


def extract_test_email_features(mail_dir, dictionary):
    features_matrix = np.zeros((1, 3000))
    docID = 0;
    '''
    words = mail_dir.split()
    for word in words:
        wordID = 0
        for i, d in enumerate(dictionary):
            if d[0] == word:
                wordID = i
                features_matrix[docID, wordID] = words.count(word)
    '''
    words = []
    for string in mail_dir:
        words += string.split()

    for word in words:
        wordID = 0
        for i, d in enumerate(dictionary):
            if d[0] == word:
                wordID = i
                features_matrix[docID, wordID] = words.count(word)

    return features_matrix

        
#1-->spam
#0-->ham
#reture the feature of the training set
def feature_to_file(train_dir = None):
    train_dir = 'ling-spam\\train-mails'
    dictionary = make_Dictionary(train_dir)

    # Prepare feature vectors per training mail and its labels   
    train_matrix = extract_features(train_dir, dictionary)
    df = pd.DataFrame(train_matrix)
    df.to_csv('feature_result.csv', header = None, index = None)
    #use navie bayes model
    return train_matrix
    

def train(train_matrix):
    train_dir = 'ling-spam\\train-mails'
    dictionary = make_Dictionary(train_dir)
    train_labels = np.zeros(702)
    train_labels[351:701] = 1
    model = MultinomialNB()
    model.fit(train_matrix, train_labels)

    return model, dictionary

#test the mail for spam
def judge(test_dir, model, dictionary):
    test_matrix = extract_test_email_features(test_dir, dictionary)
    #test_label = np.zeros(1)
    result = model.predict(test_matrix)
    #result_matrix = confusion_matrix(test_label, result)
    return result
