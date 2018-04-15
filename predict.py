# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 11:44:58 2018

@author: Siru
"""
import os
path = 'E:\\1_1social_media_computing\\cs4242-mini-project-master'
os.chdir(path)
import numpy as np
from keras.models import load_model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.util import ngrams

def lstm_response(input_text):
    labels = ['exit message','greeting','question','question ask attribute','question buy','question celebrity','question do not like earlier show result','question do not like n show result','question do not like show result','question filter results','question go with','question like earlier show result','question like n show result','question like show result','question show orientation','question show similar to','question sort results','question suited for','repeat question','switch synse','user info']
    model = load_model('intent_lstm.pkl')
    tk = Tokenizer()
    tk.fit_on_texts(input_text)
    index_list = tk.texts_to_sequences(input_text)
    x_train = pad_sequences(index_list, maxlen=64)
    predict = model.predict(x_train)
    predict = labels[np.argmax(np.bincount(predict.argmax(axis=-1)))]
    return predict

def lstm_intent(input_text):
    labels = ['both','nothing','text']
    model = load_model('response_lstm.pkl')
    tk = Tokenizer()
    tk.fit_on_texts(input_text)
    index_list = tk.texts_to_sequences(input_text)
    x_train = pad_sequences(index_list, maxlen=64)
    predict = model.predict(x_train)
    predict = labels[np.argmax(np.bincount(predict.argmax(axis=-1)))]
    return predict

def svm_intent(input_text):
    model = joblib.load('intent_svm.pkl')
    voc = joblib.load('intent_vocabulary.pkl')
    idf = joblib.load('intent_idf.pkl')
    unigram = input_text.strip().split(' ')
    bigram = [i + ' ' + j for (i,j) in ngrams(input_text.strip().split(' '),2)]
    x = unigram + bigram
    x = np.array(np.sum(TfidfVectorizer(vocabulary=voc).fit_transform(x),axis=0))[0]
    x = np.multiply(x,idf).reshape((1,idf.shape[0]))
    result = model.predict(x)
    return result[0]

def svm_response(input_text):
    model = joblib.load('response_svm.pkl')
    voc = joblib.load('vocabulary.pkl')
    idf = joblib.load('idf.pkl')
    unigram = input_text.strip().split(' ')
    bigram = [i + ' ' + j for (i,j) in ngrams(input_text.strip().split(' '),2)]
    x = unigram + bigram
    x = np.array(np.sum(TfidfVectorizer(vocabulary=voc).fit_transform(x),axis=0))[0]
    x = np.multiply(x,idf).reshape((1,idf.shape[0]))
    result = model.predict(x)
    return result[0]

