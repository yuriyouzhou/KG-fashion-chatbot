import numpy as np
from os import path
def find_class(vec, root_path):
    ids = np.argsort(vec)[-3:]
    print ids
    category_name = load_category_list(root_path)
    results = []
    for id in ids:
        results.append(category_name[id])
    return list(set(results))

def find_similar_image(vec, root_path):
    print "here"
    with open(path.join(root_path, "img_feat", "images_vgg_Fea.npy"), 'r') as f:
        vgg_feat = np.load(f)
        vgg_feat = vgg_feat[:,2048:]
    with open(path.join(root_path, "img_feat", "images_vgg_name.npy"), 'r') as f:
        vgg_name = np.load(f)
    print vgg_feat.shape, vec.T.shape, np.dot(vgg_feat, vec.T).shape
    ids = np.argsort(np.dot(vgg_feat, vec.T))[-5:]
    img_path, category, id_arr = [], [], []
    for id in ids:
	print id, vgg_name[id]
        img_path.append(vgg_name[id])
        curr_category, curr_id = vgg_name[id].split("/")[2:4]
        category.append(curr_category)
        id_arr.append(curr_id.split("_")[0])
    return img_path, category, id_arr


def load_category_list(root_path):
    with open(path.join(root_path, "img_feat", "idx2label.txt"), 'r') as f:
        lines = f.readlines()
        category = []
        for l in lines:
            category.append(l.split()[-1])
        return category

def shrink_vgg_feat():
    with open(path.join(".", "img_feat", "images_vgg_Fea.npy"), 'r') as f:
        vgg_feat = np.load(f)
        np.save("./img_feat/images_vgg_Fea_shrink.npy", vgg_feat[:, :2048])
if __name__ == '__main__':

    # shrink_vgg_feat()

    image_feature = np.random.uniform(-1, 1, size=2137)

    img_vec, category_vec = image_feature[:2048], image_feature[2048:]

    print "predicted class are %s" % ', '.join(find_class(category_vec, "."))
    print "most similar image is at %s with category %s and ID %s" % find_similar_image(category_vec, ".")

