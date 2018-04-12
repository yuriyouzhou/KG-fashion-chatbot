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

def get_response(input_text):
    model = load_model('intent_lstm.pkl')
    tk = Tokenizer()
    tk.fit_on_texts(input_text)
    index_list = tk.texts_to_sequences(input_text)
    x_train = pad_sequences(index_list, maxlen=64)
    predict = model.predict(x_train)
    predict = np.argmax(np.bincount(predict.argmax(axis=-1)))
    return predict

def get_intent(input_text):
    model = load_model('response_lstm.pkl')
    tk = Tokenizer()
    tk.fit_on_texts(input_text)
    index_list = tk.texts_to_sequences(input_text)
    x_train = pad_sequences(index_list, maxlen=64)
    predict = model.predict(x_train)
    predict = np.argmax(np.bincount(predict.argmax(axis=-1)))
    return predict
