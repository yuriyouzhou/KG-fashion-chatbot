from nltk import word_tokenize, bigrams, trigrams, ngrams
def load_leaves():
    with open("fashion-copy.csv") as input_f:
        lines = input_f.readlines()
        leaves = {}
        for l in lines:
            leaf = l.strip().split(".")[-1][:-1]
            if len(leaf.split()) > 1:
                bi_leaf = list(bigrams(leaf.split()))[0]
                leaves[bi_leaf] = leaf
            else:
                leaves[leaf] = leaf
        return leaves

def load_taxonomy():
    with open("fashion-copy.csv") as input_f:
        lines = input_f.readlines()[1:]
        inter_node = {}
        nodes = []
        for l in lines:
            tokens = l[:-1].split(".")
            l = len(tokens)
            for i,t in enumerate(tokens):
                t = t.replace(",", "")
                if t not in nodes:
                    nodes.append(t)
                if i < l-1:
                    if t not in inter_node:
                        inter_node[t] = [tokens[i+1]]
                    else:
                        if tokens[i+1] not in inter_node[t]:
                            inter_node[t].append(tokens[i+1])
        return inter_node, nodes


def load_synonym():
    with open("synonym.txt", 'r') as f:
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

def taxonomy_classify(sentence):
    tokens = word_tokenize(sentence)
    bg = bigrams(tokens)
    tg = trigrams(tokens)

    for t in tg:
        if t in syn_dict:
            return syn_dict[t]


    for t in bg:
        if t in leaves:
            return leaves[t]
        if t in syn_dict:
            return syn_dict[t]


    for t in tokens:
        if t in all_nodes:
            return t
        if t in syn_dict:
            return syn_dict[t]


if __name__ == '__main__':
    leaves = load_leaves()
    inter2leaf, all_nodes = load_taxonomy()
    syn_dict = load_synonym()


    while True:
        try:
            utterence = raw_input("Please talk to me: ")
            node = taxonomy_classify(utterence)
            if node :
                print node
            else:
                print("not found")

        except ValueError:
            print("Sorry, I didn't understand that.")
            continue

