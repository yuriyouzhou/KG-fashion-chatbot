# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import csv
import pickle
import re
from os import path
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.corpus import stopwords
import numpy as np
from nltk.tokenize import word_tokenize
from nltk import PorterStemmer
from PIL import Image
from sklearn.externals import joblib
import os
porter = PorterStemmer()
img_dir = '/storage/lzliao/knowfashion_bot/3_taxonomy_traverse/output/product_images_123325/'


COLOR = ['beige','black','blue','brown','green','grey','navy','orange','pink','purple','red','white','yellow','animal','camouflage','dotted','floral','striped','multi']
MATERIAL = ['cotton','leather','linen','wool','denim','laces','mesh','velvet','satin','faux fur','nylon']
OCCASION = ['casual','work','party','beach','school','maternity','active','wedding','sexy','bohemian']
GENDER = ['men','women','baby','kid']
SEASON = ['spring','summer','autumn','winter']

attr_names = ['ID','genders', 'seasons', 'colors', 'materials', 'occasions', 'brand', 'necks', 'sleeves', 'category', 'price']

def txt2csv():
    with open("attributes_65572.txt") as f:
        with open("attributes.csv", 'w') as writer:
            results = csv.writer(writer)
            attributes = json.loads(f.readline())
            for item in attributes['products']:
                out = [item['ID'], item['brand'], item['price'],
                item['genders'], item['colors'], item['materials'],
                item['occasions'], item['necks'], item['sleeves'],
                item['texts'], item['category']]
                results.writerow(out)


def inverted_index(attr_name):
    index_dict = {}
    unique_v = 0
    with open("attributes_65572.txt") as f:
        attributes = json.load(f)
        for product in attributes['products']:
            v = product[attr_name]
            if not isinstance(v, (list,)):
                v = [v]
            for elm in v:
                elm = porter.stem(elm.strip())
                if elm in index_dict:
                    index_dict[elm].append(product['ID'])
                else:
                    unique_v = unique_v + 1
                    index_dict[elm] = [product['ID']]
    print "there are %d unique attribute names in %s" % (unique_v, attr_name)

    with open("./index/"+attr_name+'_index.pkl', 'wb') as f:
        pickle.dump(index_dict, f, pickle.HIGHEST_PROTOCOL)

def attribute_index():
    for attr_name in attr_names:
        if attr_name == 'ID':
            index_dict = {}
            with open("attributes_65572.txt") as f:
                attributes = json.load(f)
                for i, product in enumerate(attributes['products']):
                    v = product['ID']
                    index_dict[i] = v
            with open("./index/" + attr_name + '_index.pkl', 'wb') as f:
                pickle.dump(index_dict, f, pickle.HIGHEST_PROTOCOL)
        elif attr_name == 'price':
            index_dict = {}
            with open("attributes_65572.txt") as f:
                attributes = json.load(f)
                for product in attributes['products']:
                    v = product['ID']
                    p = product['price']
                    index_dict[v] = p
            with open('./index/id2price_index.pkl', 'wb') as f:
                pickle.dump(index_dict, f, pickle.HIGHEST_PROTOCOL)
        else:
            inverted_index(attr_name)

def build_tf_idf():
    # test_set = ["The sun in the sky is bright."]  # Query
    print "loading corpus..."
    train_set = load_corpus()
    train_set = train_set
    print len(train_set)
    stopWords = stopwords.words('english')


    vectorizer = CountVectorizer(stop_words=stopWords)
    vectorizer.fit(train_set)
    joblib.dump(vectorizer, "vectorizer.sav")

    transformer = TfidfTransformer()
    print "vectorising corpus..."
    trainVectorizerArray = vectorizer.transform(train_set).toarray()

    print "tfidf transforming..."
    transformer.fit(trainVectorizerArray)
    joblib.dump(transformer, 'tfidf_transformer.sav')

    train_corpus = transformer.transform(trainVectorizerArray)
    np.save("train_corpus.npy", train_corpus.todense())
    print 'corpus', train_corpus.shape


def load_tfidf_model(root_path):
    vectorizer = joblib.load(root_path+"/attribute_detection/vectorizer.sav")
    transformer = joblib.load(root_path+"/attribute_detection/tfidf_transformer.sav")
    corpus = np.load(root_path+"/attribute_detection/train_corpus.npy")
    return vectorizer, transformer, corpus

def load_corpus():
    if not path.exists("text_corpus.txt"):
        extract_text()
    with open("text_corpus.txt") as f:
        return f.readlines()

def clean_text(str):
    def rm_repeat_chars(str):
        return re.sub(r'(.)(\1){2,}', r'\1\1', str)

    def rm_time(str):
        return re.sub(r'[0-9][0-9]:[0-9][0-9]', '', str)

    def rm_punctuation(current_tweet):
        return re.sub(r'[^\w\s]', '', current_tweet)

    def rm_digit(str):
        return re.sub("^\d+\s|\s\d+\s|\s\d+$", '', str)

    def rm_char(str):
        return ' '.join([w for w in str.split() if len(w) > 1])

    def rm_underscore(str):
        return ' '.join([w for w in str.split() if '_' not in w])

    str = str.lower()
    str = rm_repeat_chars(str)
    str = rm_time(str)
    str = rm_punctuation(str)
    str = rm_digit(str)
    str = rm_char(str)
    str = rm_underscore(str)
    
    tokens = word_tokenize(str)
    str = ' '.join([porter.stem(t) for t in tokens])
    return str

def extract_text():
    with open("attributes_65572.txt") as f:
        with open("text_corpus.txt", 'w') as writer:
            attributes = json.load(f)
            for product in attributes['products']:
                v = product['texts']
                v = clean_text(v)
                writer.write(v+"\n")



def extract_price(sent):
    return re.findall('\d+', sent)




def search_by_price(price):
    with open("attributes_65572.txt") as f:
        attributes = json.load(f)
        results = []
        for product in attributes['products']:
            v = float(product['price'])
            if abs(price - v) < 50:
                results.append(product['ID'])
        return results

def imgid2path():
    category = os.listdir(img_dir)
    id2path = {}
    for c in category:
        img_names = os.listdir(path.join(img_dir, c))
        for n in img_names:
            id = n.split("_")[0]
            id2path[id] = path.join(img_dir, c, n)
    return id2path

def prepare_data():
    attribute_index()
    build_tf_idf()

def detect_attribute(sent, root_path):
    def detect_attr(sent):
        tokens = word_tokenize(sent)
        tokens = [porter.stem(v) for v in tokens]


        # attribute query
        results = []
        intersect_result = set()
        detected_attr_dict = {}
        for t in tokens:
            if t in brand_idx:
                results += brand_idx[t]
                if len(intersect_result) > 0:
                    intersect_result = intersect_result.intersection(brand_idx[t])
                else:
                    intersect_result = set(brand_idx[t])
                detected_attr_dict["brand"] = t
            if t in category_idx:
                results += category_idx[t]
                if len(intersect_result) > 0:
                    intersect_result = intersect_result.intersection(category_idx[t])
                else:
                    intersect_result = set(category_idx[t])
                detected_attr_dict["category"] = t
            if t in color_idx:
                results += color_idx[t]
                if len(intersect_result) > 0:
                    intersect_result = intersect_result.intersection(color_idx[t])
                else:
                    intersect_result = set(color_idx[t])
                detected_attr_dict["colors"] = t
            if t in gender_idx:
                results += gender_idx[t]
                if len(intersect_result) > 0:
                    intersect_result = intersect_result.intersection(gender_idx[t])
                else:
                    intersect_result = set(gender_idx[t])
                detected_attr_dict["genders"] = t
            if t in material_idx:
                results += material_idx[t]
                if len(intersect_result) > 0:
                    intersect_result = intersect_result.intersection(material_idx[t])
                else:
                    intersect_result = set(material_idx[t])
                detected_attr_dict["materials"] = t
            if t in necks_idx:
                results += necks_idx[t]
                if len(intersect_result) > 0:
                    intersect_result = intersect_result.intersection(necks_idx[t])
                else:
                    intersect_result = set(necks_idx[t])
                detected_attr_dict["necks"] = t
            if t in occasion_idx:
                results += occasion_idx[t]
                if len(intersect_result) > 0:
                    intersect_result = intersect_result.intersection(occasion_idx[t])
                else:
                    intersect_result = set(occasion_idx[t])
                detected_attr_dict["occasions"] = t
            if t in season_idx:
                results += season_idx[t]
                if len(intersect_result) > 0:
                    intersect_result = intersect_result.intersection(season_idx[t])
                else:
                    intersect_result = set(season_idx[t])
                detected_attr_dict["seasons"] = t
            if t in sleeves_idx:
                results += sleeves_idx[t]
                if len(intersect_result) > 0:
                    intersect_result = intersect_result.intersection(sleeves_idx[t])
                else:
                    intersect_result = set(sleeves_idx[t])
                detected_attr_dict["sleeves"] = t


        return detected_attr_dict, list(set(results)), list(intersect_result)

    def tfidf_retrieval(query):
        testVectorizerArray = vectorizer.transform([query]).toarray()
        print 'Transform Vectorizer to test set', len(testVectorizerArray), testVectorizerArray

        print 'fitting...'

        transformer.fit(testVectorizerArray)

        print 'transforming...'
        tfidf = transformer.transform(testVectorizerArray)
        tfidf = tfidf.todense()

        print 'matching...'
        test = tfidf
        return id_idx[np.argmax(np.dot(corpus, test.T))]
    vectorizer, transformer, corpus = load_tfidf_model(root_path)

    def load_index(attr):
        with open(path.join(root_path, 'attribute_detection', 'index', attr+'_index.pkl'), 'rb') as f:
            return pickle.load(f)

    brand_idx = load_index('brand')
    category_idx = load_index('category')
    color_idx = load_index('colors') #
    gender_idx = load_index('genders') #
    material_idx = load_index('materials') #
    necks_idx = load_index('necks')
    occasion_idx = load_index('occasions') #
    season_idx = load_index('seasons') #
    sleeves_idx = load_index('sleeves')
    id_idx = load_index('ID')
    id2price_idx = load_index('id2price')

    BRAND, CATEGORY, NECKS, SLEEVES  = [], [], [], []
    for k in brand_idx:
        BRAND.append(k)
    for k in category_idx:
        CATEGORY.append(k)
    for k in necks_idx:
        NECKS.append(k)
    for k in sleeves_idx:
        SLEEVES.append(k)

    def detect_keyword(sent):
        attr_names_dict = {
            'genders': 'genders',
            'gender': 'genders',
            'seasons': 'seasons',
            'season': 'seasons',
            'colors': 'colors',
            'color': 'colors',
            'colour': 'color',
            'materials': 'materials',
            'material': 'materials',
            'occasions': 'occasions',
            'occasion': 'occasions',
            'brand': 'brand',
            'necks': 'necks',
            'neck': 'necks',
            'sleeves': 'sleeves',
            'sleeve': 'sleeves',
            'category': 'category',
            'price': 'price'
        }
        tokens = sent.split()
        keywords = []
        for t in tokens:
            if t in attr_names_dict:
                keywords.append(attr_names_dict[t])
        return keywords
    def detect_orientation(sent):
        # detect orientation
        tokens = sent.split()
        orientation = ['look', 'back', 'right', 'left', 'top']
        orientation_keyword = None
        for t in tokens:
            if t in orientation:
                orientation_keyword = t
        return orientation_keyword

    detected_attr_dict, results, intersect_results = detect_attr(sent)
    # text_results = tfidf_retrieval(sent)
    attr_keyword = detect_keyword(sent)
    orien_keyword = detect_orientation(sent)
    return attr_keyword, detected_attr_dict, intersect_results, orien_keyword

def filter_by_attr(attr_dict, root_path):
    print attr_dict
    with open(path.join(root_path, 'attribute_detection', "attributes_65572.txt")) as f:
        attributes = json.load(f)
        results = []
        for product in attributes['products']:
            if product['category'] == 'a-line':
                product['category'] = 'a-lin'
            is_match = True
            for attr in product:
                attr = str(attr)
                if attr in attr_dict and product[attr] != attr_dict[attr]:
                    is_match = False
            if is_match:
                results.append(product['ID'])
        return results

def get_attr_dict_by_id(ID, root_path):
    with open(path.join(root_path, 'attribute_detection', "attributes_65572.txt")) as f:
        attributes = json.load(f)
        attr_dict = {}
        attr_list =['genders', 'seasons', 'colors', 'materials', 'occasions', 'brand', 'necks', 'sleeves', 'category']

        for product in attributes['products']:
            if product['ID'] == ID:
                for attr in attr_list:
                    attr_dict[attr] = product[attr]
        return attr_dict

if __name__ == '__main__':
    while True:
        utterence = raw_input("Please talk to me: ")
        detect_attr_keyword, detect_attr_dict, intersect_result = detect_attribute(utterence, ".")
        print detect_attr_keyword
        if detect_attr_dict:
            for attr in detect_attr_dict:
                print "detect " + attr + " with value " + detect_attr_dict[attr]
            print "intersection result is ", len(intersect_result), intersect_result
        else:
            print("not found")

