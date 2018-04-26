# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 10:24:07 2018

@author: Siru
"""

import os
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import KFold
from sklearn.svm import LinearSVC
from sklearn.metrics import precision_score,recall_score,classification_report
import numpy as np
from sklearn.externals import joblib

path = 'E:\\1_1social_media_computing\\cs4242-mini-project-master'
os.chdir(path)

def loading_process(x):
    x = x.strip()
    if x[0] == '‘':
        x = x[1:]
    if x[-1] == '’':
        x = x[:-1]
    return x

def intent_model_svm():
    label = []
    #image = []
    text = []
    with open('processed_data_train.csv') as file:
        lines = csv.reader(file)
        for line in lines:
            if line[0] != '':
                label.append(line[0])
            #image.append(line['image'])
                text_tmp = loading_process(line[2])
                text.append(text_tmp)
    label = np.array(label)
    text = np.array(text)
    pipe = TfidfVectorizer(ngram_range=(1,2))
    x_feats = pipe.fit_transform(text)
    vocabulary = pipe.vocabulary_
    intent_idf = pipe.idf_
    #performance evaluation
    for c in np.arange(1,10,0.5):
        avg_p = 0
        avg_r = 0
        k_fold = KFold(n_splits=10,random_state=1)
        for train_index,test_index in k_fold.split(x_feats):
            model = LinearSVC(C=c).fit(x_feats[train_index],label[train_index])
            predicts = model.predict(x_feats[test_index])
            #print(classification_report(label[test_index],predicts))
            avg_p	+= precision_score(label[test_index],predicts, average='macro')
            avg_r	+= recall_score(label[test_index],predicts, average='macro')
    
        print('Average Precision is %f.' %(avg_p/10.0))
        print('Average Recall is %f.' %(avg_r/10.0))
        print(c)
    #best model comes with C = 4.5
    model = LinearSVC(C = 4.5).fit(x_feats,label)
    joblib.dump(model, 'intent_svm.pkl')
    joblib.dump(vocabulary, 'intent_vocabulary.pkl')
    joblib.dump(intent_idf, 'intent_idf.pkl')

def response_model_svm():
    label = []
    #image = []
    text = []
    with open('processed_data_train.csv') as file:
        lines = csv.reader(file)
        for line in lines:
            if line[0] != '':
                label.append(line[3])
            #image.append(line['image'])
                text_tmp = loading_process(line[2])
                text.append(text_tmp)
    label = np.array(label)
    text = np.array(text)
    idx = label=='text'
    sample = label[idx]
    label = label[~idx]
    text_sample = text[idx]
    text = text[~idx]
    idx = np.random.randint(0,sample.shape[0],size = label.shape)
    sample = sample[idx]
    text_sample = text_sample[idx]
    label = np.hstack((label,sample))
    text = np.hstack((text,text_sample))
    text = np.vstack((text,label))
    idx = np.random.randint(0,text.shape[1],size =text.shape[1] )
    label = text[1,idx]
    text = text[0,idx]
    pipe = TfidfVectorizer(ngram_range=(1,2))
    x_feats = pipe.fit_transform(text)
    vocabulary = pipe.vocabulary_
    idf = pipe.idf_
    #performance evaluation
    for c in np.arange(0.2,2,0.2):
        avg_p = 0
        avg_r = 0
        k_fold = KFold(n_splits=10,random_state=1)
        for train_index,test_index in k_fold.split(x_feats):
            model = LinearSVC(C = c).fit(x_feats[train_index],label[train_index])
            predicts = model.predict(x_feats[test_index])
            #print(classification_report(label[test_index],predicts))
            avg_p	+= precision_score(label[test_index],predicts, average='macro')
            avg_r	+= recall_score(label[test_index],predicts, average='macro')
    
        print('Average Precision is %f.' %(avg_p/10.0))
        print('Average Recall is %f.' %(avg_r/10.0))
        print(c)
    #best model comes with C = 0.2
    model = LinearSVC(C = 0.2).fit(x_feats,label)
    joblib.dump(model, 'response_svm.pkl')
    joblib.dump(vocabulary,'vocabulary.pkl')
    joblib.dump(idf,'idf.pkl')
    
if __name__=='__main__':
    intent_model_svm()
    response_model_svm()
