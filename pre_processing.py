# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 20:24:17 2018

@author: Siru
"""

import os
import zipfile
import json
import re
import csv

# path = 'E:\\1_1social_media_computing\\cs4242-mini-project-master\\dataset-20180326T122551Z-001\\dataset'
# os.chdir(path)

def split_data(x,settype):
    if x.endswith('.json') and re.findall(settype,x):
        return True
    else:
        return False

def check_bracket(x):
    while len(re.findall('}',x)) < 2:
        x = x + '}'
    return x

def extract_data(x):
    tmp = x.split('},')
    tmp = [each.strip() for each in tmp]
    final = []
    for each in tmp:
        if "speaker" in each:               
            each = check_bracket(each)
            segment = json.loads(each)
        else:
            continue
        if segment['speaker'] =='user':
            user_text = segment['utterance']['nlg']
            user_image = 1 * ((segment['utterance']['images']) is not None)
            user_label = segment['type']
            if user_label =='question':
                try:
                    sub_type = segment['question-type']
                    user_label = user_label + '_' +sub_type
                except:
                    KeyError
                    #print(each) 
            result = {'user_image':user_image,'user_label':user_label,'user_text':user_text}
            final.append(result.copy())
        elif segment['speaker'] =='system':
            try:
                sys_image = 1 * ((segment['utterance']['images']) is not None)
                sys_text = segment['utterance']['nlg']
            except:
                KeyError
                #print(each)
            result = final.pop()
            if 'sys_image' in result:
                result['sys_image'] = [sys_image]+ result['sys_image']
            else:
                result['sys_image'] = [sys_image]
            if 'sys_text' in result:
                result['sys_text'].append(sys_text)
            else:
                result['sys_text'] = [sys_text]
            final.append(result)
    return final

def sys_response(image,text):
    result = ''
    len_img = len(image)
    len_text = len(text)
    if len_image and len_text:
        result = 'both'
    elif len_image>0 and len_text ==0:
        result = 'image'
    elif len_image ==0 and len_text >0:
        result = 'text'
    else:
        raise ValueError
        print(image,text)
    return result

def main():
    with zipfile.ZipFile('dataset.zip','r') as f:
        dataset = [split_data(x,'train') for x in f.namelist()]
        outfile = []
        counter = 0
        for each in dataset:
            if each:
                tmp = f.open(f.namelist()[counter]).read().decode()[1:-1].strip()
                outfile.append(tmp)
            counter += 1
    
    clean_data = []
    i = 0
    for file in outfile:
        i += 1 
        tmp = extract_data(file)
        clean_data.append(tmp)
        if i > 1000:
            break
    dataset = 'train'
    with open('processed_data_'+dataset+'.csv','w',newline='') as writer:
        results = csv.writer(writer)
        for j in clean_data:
            for i in j:
                label = i['user_label']
                img = i['user_image']
                text = i['user_text']
                system_reply = sys_response(i['sys_image'],i['sys_text'])
                out = [label,img,text,system_reply]
                results.writerow(out)

if __name__=='__main__':
    main()
