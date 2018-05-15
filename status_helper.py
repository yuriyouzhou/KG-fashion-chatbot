import json
def initialise_state():
    with open('./history/status.json', 'w') as f:
        state = {
                "current_node": "fashion",
                "is_leaf_node": False,
                "missing_attr": [''],
                "informed_attr": [''],
                "curr_id": None}
        
        f.write(json.dumps(state))

def load_state():
    with open('./history/status.json') as f:
        return json.load(f)
initialise_state()
state = load_state()
print state['current_node']

