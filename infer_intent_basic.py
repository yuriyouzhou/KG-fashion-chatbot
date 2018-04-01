import os
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import KFold
from sklearn.svm import LinearSVC
from sklearn.metrics import precision_score,recall_score
import numpy as np

path = 'E:\\1_1social_media_computing\\cs4242-mini-project-master'
os.chdir(path)

def loading_process(x):
    x = x.strip()
    if x[0] == '‘':
        x = x[1:]
    if x[-1] == '’':
        x = x[:-1]
    return x

def infer_intent(x):
    label = []
    image = []
    text = []
    with open('processed_data_train.csv') as file:
        lines = csv.DictReader(file)
        for line in lines:
            label.append(line['type'])
            #image.append(line['image'])
            text_tmp = loading_process(line['text'])
            text.append(text_tmp)
    text.append(loading_process(x))
    x_feats = TfidfVectorizer(ngram_range=(1,2)).fit_transform(text)
    label = np.array(label)
    #performance evaluation
    # avg_p = 0
    # avg_r = 0
    # k_fold = KFold(n_splits=10,random_state=1)
    # for train_index,test_index in k_fold.split(x_feats):
    #     model = LinearSVC().fit(x_feats[train_index],label[train_index])
    #     predicts = model.predict(x_feats[test_index])
    #     #print(classification_report(y[test],predicts))
    #     avg_p	+= precision_score(label[test_index],predicts, average='macro')
    #     avg_r	+= recall_score(label[test_index],predicts, average='macro')

    # print('Average Precision is %f.' %(avg_p/10.0))
    # print('Average Recall is %f.' %(avg_r/10.0))
    model = LinearSVC().fit(x_feats[0:-1],label)
    output = model.predict(x_feats[-1])
    return output


if __name__=='__main__':
    userText = 'Could you recommend some similar shoes to this one?'
    intent = infer_intent(userText)
    print('The intent is {}'.format(intent))
