# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 11:44:58 2018

@author: Siru
"""
import os
# path = 'E:\\1_1social_media_computing\\cs4242-mini-project-master'
# os.chdir(path)
import numpy as np
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.util import ngrams
from os import path

def svm_intent(input_text, curr_path):
    model = joblib.load(path.join(curr_path, 'intention_model', 'intent_svm.pkl'))
    voc = joblib.load(path.join(curr_path, 'intention_model', 'intent_vocabulary.pkl'))
    idf = joblib.load(path.join(curr_path, 'intention_model', 'intent_idf.pkl'))
    unigram = input_text.strip().split(' ')
    bigram = [i + ' ' + j for (i,j) in ngrams(input_text.strip().split(' '),2)]
    x = unigram + bigram
    x = np.array(np.sum(TfidfVectorizer(vocabulary=voc).fit_transform(x),axis=0))[0]
    x = np.multiply(x,idf).reshape((1,idf.shape[0]))
    result = model.predict(x)
    return result[0]

def svm_response(input_text, curr_path):
    model = joblib.load(path.join(curr_path,'intention_model','response_svm.pkl'))
    voc = joblib.load(path.join(curr_path,'intention_model', 'response_vocabulary.pkl'))
    idf = joblib.load(path.join(curr_path, 'intention_model','response_idf.pkl'))
    unigram = input_text.strip().split(' ')
    bigram = [i + ' ' + j for (i,j) in ngrams(input_text.strip().split(' '),2)]
    x = unigram + bigram
    x = np.array(np.sum(TfidfVectorizer(vocabulary=voc).fit_transform(x),axis=0))[0]
    x = np.multiply(x,idf).reshape((1,idf.shape[0]))
    result = model.predict(x)
    return result[0]

