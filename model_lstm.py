# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 18:52:19 2018

@author: Siru
"""
import numpy as np
import csv
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Embedding
from keras.layers import LSTM,Bidirectional
from sklearn.preprocessing import LabelBinarizer
from keras.preprocessing.text import Tokenizer

def loading_process(x):
    x = x.strip()
    if x[0] == '‘':
        x = x[1:]
    if x[-1] == '’':
        x = x[:-1]
    return x

def load_data(y):
    label = []
    image = []
    text = []
    with open(data_dir) as file:
        lines = csv.reader(file)
        for line in lines:
            if y =='response':
                label.append(line[3])
            elif y == 'intent':
                label.append(line[0])
            else:
                raise ValueError
                print('Label can only be response or intent')
            #image.append(line['image'])
            text_tmp = loading_process(line[2])
            text.append(text_tmp)
    label = np.array(label)
    text = np.array(text)
    text = np.vstack((label,text)).T
    np.random.shuffle(text)
    x_train = text[0:round(0.85*len(label)),1]
    x_test = text[round(0.85*len(label)):,1]
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(text[:,1]) 
    x_train = tokenizer.texts_to_sequences(x_train)
    x_test = tokenizer.texts_to_sequences(x_test)
    encoder = LabelBinarizer()
    y_train = text[0:round(0.85*len(label)),0]
    y_train = encoder.fit_transform(y_train)
    y_test = text[round(0.85*len(label)):,0]
    y_test = encoder.fit_transform(y_test)
    return x_train, y_train,x_test,y_test


data_dir = 'processed_data_train.csv'
max_features = 20000
maxlen = 80  # cut texts after this number of words (among top max_features most common words)
batch_size = 32

print('Loading data...')
x_train, y_train,x_test,y_test = load_data('response')
print(len(x_train), 'train sequences')
print(len(x_test), 'test sequences')

print('Pad sequences (samples x time)')
x_train = sequence.pad_sequences(x_train, maxlen=maxlen)
x_test = sequence.pad_sequences(x_test, maxlen=maxlen)
print('x_train shape:', x_train.shape)
print('x_test shape:', x_test.shape)

print('Build model...')
model = Sequential()
model.add(Embedding(max_features, 64))
model.add(Bidirectional(LSTM(128, dropout=0.2, recurrent_dropout=0.2)))
#configure to 21 for intent model
model.add(Dense(3, activation='sigmoid'))


# try using different optimizers and different optimizer configs
model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

print('Train...')
model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=1,
          validation_data=(x_test, y_test))
score, acc = model.evaluate(x_test, y_test,
                            batch_size=batch_size)
print('Test score:', score)
print('Test accuracy:', acc)

model.save('./response_lstm.pkl')
