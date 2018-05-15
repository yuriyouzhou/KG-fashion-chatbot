import os
from os import path
def imgid2path(img_dir):
    category = os.listdir(img_dir)
    id2path = {}
    for c in category:
        img_names = os.listdir(path.join(img_dir, c))
        for n in img_names:
            id = n.split("_")[0]
            id2path[id] = path.join("./product_images_123325/", c, n)
    return id2path

def get_img_by_id(id, root_path):
    id = id.strip()
    id2path = imgid2path(path.join(root_path, 'product_images_123325/'))
    return id2path[id]


if __name__ == '__main__':
    print get_img_by_id('B00A7AFB84', '.')
