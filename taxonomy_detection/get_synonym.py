from urllib import quote_plus
import urllib2
import re
from locate_taxonomy import load_taxonomy
from bs4 import BeautifulSoup as BS
import pickle


def get_search_result(key):
    page = urllib2.urlopen('http://www.thesaurus.com/browse/%s'%quote_plus(key)).read()
    soup = BS(page)
    # for ultag in soup.find_all('ul', {'class': 'css-slo9t5 er7jav80'}):
    words = []
    ultag = soup.find_all('ul', {'class': 'css-slo9t5 er7jav80'})[0]
    for litag in ultag.find_all('li'):
        if '{' in litag.text:
            text = litag.text.split("}")[-1]
            words.append(text)
        else:
            words.append(litag.text)
    return words

def find_synonym():
    _, nodes = load_taxonomy()
    synonym_dict = {}
    for t in nodes:
        print "query %s..." % t
        try:
            res = get_search_result(t)
            synonym_dict[t] = [str(v) for v in res] + [t]
        except:
            print "cannot query %s" % t
    with open("synonym.txt", 'w') as f:
        for t in nodes:
            if t in synonym_dict:
                f.write("%s||||%s\n"%(t, ",".join(synonym_dict[t])))
            else:
                f.write("%s||||\n"%t)


if __name__ == '__main__':
    find_synonym()
    # res = get_search_result('bag')
    # print ','.join(res)
