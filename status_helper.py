import json
from os import path
def initialise_state(root_path):
    with open(path.join(root_path, './history/status.json'), 'w') as f:
        state = {
                "current_node": "fashion",
                "is_leaf_node": False,
                "missing_attr": [''],
                "informed_attr": [''],
                "product_id": None}

        f.write(json.dumps(state))

def load_state():
    with open('./history/status.json') as f:
        return json.load(f)
if __name__ == '__main__':
    initialise_state()
    state = load_state()
    print state['current_node']

