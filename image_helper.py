import numpy as np
from os import path
def find_class(vec, root_path):
    ids = np.argsort(vec)[:3]
    category_name = load_category_list(root_path)
    results = []
    for id in ids:
        results.append(category_name[id])
    return results

def find_similar_image(vec, root_path):
    with open(path.join(root_path, "img_feat", "images_vgg_Fea_shrink.npy"), 'r') as f:
        vgg_feat = np.load(f)
    with open(path.join(root_path, "img_feat", "images_vgg_name.npy"), 'r') as f:
        vgg_name = np.load(f)
    id = np.argmax(np.dot(vgg_feat, vec.T))
    img_path = vgg_name[id]
    category, id = img_path.split("/")[2:4]
    id = id.split("_")[0]
    return img_path, category, id


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
    print "most similar image is at %s with category %s and ID %s" % find_similar_image(img_vec, ".")

