from nltk import word_tokenize, bigrams, trigrams, ngrams, PorterStemmer
from os import path
def load_leaves(root_path):
    # load leafs (after stemming)
    porter = PorterStemmer()
    with open(path.join(root_path, "taxonomy_detection", "fashion-copy.csv")) as input_f:
        lines = input_f.readlines()
        leaves = {}
        leaves_list = []
        leaf2id = {}

        # step 1: exact word mapping
        for line in lines:
            l, ID = line.split(",")
            leaf = l.strip().split(".")[-1]
            leaves_list.append(leaf)
            leaves[leaf] = leaf
            leaf2id[leaf] = ID

        # step 2: stemmed word mapping
        stemmed_leaf_list = []
        for leaf in leaves_list:
            stemmed_leaf = ' '.join([porter.stem(v) for v in leaf.split()])
            stemmed_leaf_list.append(stemmed_leaf)
            if leaf not in stemmed_leaf:
                leaves[stemmed_leaf] = leaf


        # step 3: bi-gram and tri-gram mapping
        for leaf in leaves_list+stemmed_leaf_list:
            l = len(leaf.split())
            if l == 2:
                bg = list(bigrams(leaf.split()))[0]
                leaves[bg] = leaf
            if l == 3:
                tg = list(trigrams(leaf.split()))[0]
                leaves[tg] = leaf

        # step 4: corner cases
        leaves[('t', 'shirt')] = 't-shirt'
        leaves[('t', 'shirts')] = 't-shirt'
        leaves[('a', 'line')] = 'a-line'
        leaves['Tshirt'] = 't-shirt'
        leaves['tshirt'] = 't-shirt'
        leaves['T-shirt'] = 't-shirt'
        leaves['camisole'] = 'camisole tank'
        leaves['cape'] = 'cape coat'
        leaves['polo'] = 'polo shirt'
        leaves['henley'] = 'henley shirt'


        return leaves, leaf2id

def load_inter_node(root_path):
    porter = PorterStemmer()
    with open(path.join(root_path, "taxonomy_detection", "fashion-copy.csv")) as input_f:
        lines = input_f.readlines()[1:]
        inter_node = {}
        for l in lines:
            l, ID = l.split(",")
            tokens = l.split(".")
            l = len(tokens)
            for i,t in enumerate(tokens):
                if i < l-1:
                    t = porter.stem(t)
                    next_t = porter.stem(tokens[i+1])
                    if t not in inter_node:
                        inter_node[t] = [next_t]
                    else:
                        if next_t not in inter_node[t]:
                            inter_node[t].append(next_t)
        return inter_node


def load_synonym(root_path):
    with open(path.join(root_path, "taxonomy_detection", "synonym.txt"), 'r') as f:
        lines = f.readlines()
        syn_dict = {}
        for l in lines:
            t, syn_tokens = l.split("||||")
            syn_tokens = syn_tokens.strip().split(",")
            for w in syn_tokens:
                n = len(w.split())
                if n == 2:
                    w = list(bigrams(w.split()))[0]
                if n == 3:
                    w = list(trigrams(w.split()))[0]
                if w not in syn_dict:
                    syn_dict[w] = [t]
                else:
                    syn_dict[w].append(t)
        # for k in syn_dict:
        #     if len(syn_dict[k]) > 1:
        #         print k, syn_dict[k]
        return syn_dict

def taxonomy_classify(sentence, root_path):
    leaves, leaf2id = load_leaves(root_path)
    inter2leaf = load_inter_node(root_path)
    syn_dict = load_synonym(root_path)


    tokens = word_tokenize(sentence)
    bg = bigrams(tokens)
    tg = trigrams(tokens)


    # step 1: check if at leaf node
    leaf_result, inter_result = [], []
    for t in tg:
        if t in leaves:
            leaf_result.append(leaves[t])
    for t in bg:
        if t in leaves:
            leaf_result.append(leaves[t])
    for t in tokens:
        if t in leaves:
            leaf_result.append(leaves[t])

    # step 2: check if at inter node
    for t in tg:
        if t in syn_dict:
            inter_result+=syn_dict[t]

    for t in bg:
        if t in syn_dict:
            inter_result+=syn_dict[t]

    for t in tokens:
        if t in inter2leaf:
            inter_result+=inter2leaf[t]
        if t in syn_dict:
            inter_result+=syn_dict[t]

    if leaf_result:
        return inter_result, leaf_result, leaf2id[leaf_result[0]]
    return inter_result, leaf_result, None


if __name__ == '__main__':
    porter = PorterStemmer()
    while True:
        utterence = raw_input("Please talk to me: ")
        utterence = ' '.join([porter.stem(v) for v in utterence.split()])
        inter_result, leaf_result, ID = taxonomy_classify(utterence, ".")
        if leaf_result :
            print "leaf result detected", leaf_result, ID
        elif inter_result:
            print "inter result detected", inter_result
        else:
            print("not found")


