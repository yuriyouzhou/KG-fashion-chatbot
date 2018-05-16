from flask import Flask, render_template, request, send_from_directory, send_file
# from flask_uploads import UploadSet, configure_uploads, IMAGES
from predict import svm_intent, svm_response
from detect_attribute import detect_attribute, filter_by_attr, get_attr_dict_by_id
from locate_taxonomy import taxonomy_classify, load_leaves
from text_task_resnet.run_prediction import run_text_prediction
from get_img_by_id import get_img_by_id
from status_helper import initialise_state
import json
from os import path
import csv
import requests


app = Flask(__name__)
# photos = UploadSet('photos', IMAGES)
# app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
# configure_uploads(app, photos)


end_response = {
    "intent_type": "exit message",
    "response_type": "ending nlg",
    "type": "exit message",
    "speaker": "system",
    "utterance": {
        "images": None,
        "false nlg": None,
        "nlg": "This conversation is over  :)"
    },
    "inference": "exit message"
}




@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/get")
def get_bot_response():
    #step 1: infer intention of the model
    msg = request.args.get('messageText')
    intent_type = svm_intent(msg, app.root_path)
    response_type = svm_response(msg, app.root_path)
    if intent_type == 'greeting':
        initialise_state(app.root_path)
        response = [ {
            "type": "greeting",
            "speaker": "system",
            "utterance": {
                "images": None,
                "false nlg": None,
                "nlg": "Hi, how can i help you with something today?"
            }
        }]
        return json.dumps(response)

    inter_child, leaf_node, leaf_sample_img_ID = taxonomy_classify(msg, app.root_path)
    attr_keywords, detect_attr_dict, intersect_result, orientation_keyword = detect_attribute(msg, app.root_path)

    state = load_state()
    print state
    state, is_attribute_manipulation = update_state(state, inter_child, leaf_node, attr_keywords, leaf_sample_img_ID, detect_attr_dict)
    print is_attribute_manipulation
    if state['is_leaf_node']:
        if is_attribute_manipulation:
            IDs = filter_by_attr(state['attr_dict'], app.root_path)
            print IDs
            if len(IDs) > 0:
                curr_id = IDs[0]
                response = [{
                    "intent_type": intent_type,
                    "response_type": response_type,
                    "speaker": "system",
                    "utterance": {
                        "images": [get_img_by_id(curr_id, app.root_path, state['current_node'])],
                        "false nlg": None,
                        "nlg": "check this %s out! you can ask more about %s" % (
                        state['current_node'][0], ', '.join(state['missing_attr']))
                    },
                    "img_text": state['current_node']
                }]
                return json.dumps(response)
            else:
                response = [{
                    "intent_type": intent_type,
                    "response_type": response_type,
                    "speaker": "system",
                    "utterance": {
                        "images": None,
                        "false nlg": None,
                        "nlg": "Sorry, we do not have such product in our record"
                    },
                    "img_text": None
                }]
                return json.dumps(response)

        elif not attr_keywords and leaf_sample_img_ID and orientation_keyword == None:
            # no attribute detected, give representative response
            print detect_attr_dict
            curr_id = leaf_sample_img_ID if leaf_sample_img_ID else state['product_id']
            response = [{
                "intent_type": intent_type,
                "response_type": response_type,
                "speaker": "system",
                "utterance": {
                    "images": [get_img_by_id(curr_id, app.root_path, state['current_node'])],
                    "false nlg": None,
                    "nlg": "check this %s out! you can ask more about %s" % (state['current_node'][0], ', '.join(state['missing_attr']))
                },
                "img_text": state['current_node']
            }]
            return json.dumps(response)
        elif state['product_id'] and orientation_keyword:
            img = get_img_by_id(state['product_id'], app.root_path, state['current_node'], orientation_keyword)
            if img != None:
                img = [img]
                nlg = "check this %s out! you can ask more about %s" % (state['current_node'][0], ', '.join(state['missing_attr']))
            else:
                nlg = "sorry we don't have such orientation~ask me more"

            response = [{
                "intent_type": intent_type,
                "response_type": response_type,
                "speaker": "system",
                "utterance": {
                    "images": img,
                    "false nlg": None,
                    "nlg": nlg
                },
                "img_text": state['current_node']
            }]
            return json.dumps(response)

        elif state['product_id']:
            # a product is located
            nlg = get_info_by_id(state['product_id'], attr_keywords)
            response = [{
                "intent_type": intent_type,
                "response_type": response_type,
                "speaker": "system",
                "utterance": {
                    "images": None,
                    "false nlg": None,
                    "nlg": nlg
                }
            }]
            return json.dumps(response)
        else:
            if len(intersect_result) <= 1000:
                # enough attributes, return some sample responses
                if len(intersect_result) >= 3:
                    results_to_show = intersect_result[:3]
                else:
                    results_to_show = intersect_result
                images = [get_img_by_id(v, app.root_path) for v in results_to_show]
                print images
                response = [{
                    "intent_type": intent_type,
                    "response_type": response_type,
                    "speaker": "system",
                    "utterance": {
                        "images": images,
                        "false nlg": None,
                        "nlg": "check these %s out! which one do you like?" % leaf_node[0]
                    }
                }]
                return json.dumps(response)
            else:
                # not enough attributes, ask for more
                attr_names = ['genders', 'seasons', 'colors', 'materials', 'occasions', 'brand', 'necks',
                              'sleeves', 'category', 'price']

                missing = []
                for k in attr_names:
                    if k not in detect_attr_dict:
                        missing.append(k)
                msg = "can you tell me more about " + ', '.join(missing)
                print missing
                response = [{
                    "intent_type": intent_type,
                    "response_type": response_type,
                    "speaker": "system",
                    "utterance": {
                        "images": None,
                        "false nlg": None,
                        "nlg": msg
                    }
                }]
                return json.dumps(response)

    if inter_child:
        # if at inter node, return traverse guid response
        print inter_child
        if len(inter_child) > 3:
            inter_child = inter_child[:3]
        msg = "Which one do you like? We have %s"% ', '.join(inter_child)
        _, leaf2id = load_leaves(app.root_path)
        imgs = [get_img_by_id(leaf2id[str(v)], app.root_path, None) for v in inter_child]
        response = [{
            "intent_type": intent_type,
            "response_type": response_type,
            "speaker": "system",
            "utterance": {
                "images": imgs,
                "false nlg": None,
                "nlg": msg
            },
            "img_text": inter_child
        }]
        return json.dumps(response)

    if "hi" == msg or "hello" == msg:
        # if this is the start of the conversation, return predifned response
        clear_history()
        pred_sent = run_text_prediction(app.root_path)[-1]
        response = [{
            "response_type": response_type,
            "intent_type":intent_type,
            "speaker": "system",
            "utterance": {
                "images": None,
                "false nlg": None,
                "nlg": pred_sent
            }
        }]
        return json.dumps(response)

    # step 2: read current msg from user and save history
    curr_turn = {
        "intent_type": intent_type,
        "response_type": response_type,
        "speaker": "user",
        "utterance": {
            "images": None,
            "false nlg": None,
            "nlg": msg
        }
    }
    with open(path.join(app.root_path, './history/curr_history.json')) as data_file:
        old_data = json.load(data_file)
        if old_data is None:
            data = [curr_turn]
        else:
            data = old_data
            data.append(curr_turn)
        with open(path.join(app.root_path, './history/curr_history.json'), 'w') as output:
            output.write(json.dumps(data))


    # step 3: run model prediction
    if "text" in response_type or "both" in response_type:
        # pred_sent = run_text_prediction(app.root_path)[-1]
        pred_sent = ' '.join(nodes)+ ' '.join(intersect_results) + ' '.join(text_result)
        response = [{
            "response_type": response_type,
            "intent_type": intent_type,
            "speaker": "system",
            "utterance": {
                "images": [get_img_by_id(text_result, app.root_path)],
                "false nlg": None,
                "nlg": pred_sent
            }
        }]
    else:
        response = [{
            "response_type": response_type,
            "intent_type": intent_type,
            "speaker": "system",
            "utterance": {
                "images": [get_img_by_id(text_result, app.root_path)],
                "false nlg": None,
                "nlg": "Image response is not ready yet"
            }
        }]
    data = data + response
    with open(path.join(app.root_path, './history/curr_history.json'), 'w') as outfile:
        outfile.write(json.dumps(data))
    print response
    return json.dumps(response)


def get_info_by_id(id, keywords):
    with open(path.join(app.root_path, 'attribute_detection', 'attributes_65572.txt'), 'r') as f:
        attributes = json.loads(f.readline())
        for item in attributes['products']:
            if id == item['ID']:
                nlg = ""
                for v in keywords:
                    v = str(v)
                    nlg += "its %s is %s"%(v, item[v])
                nlg += " it is %s" % item['texts']
                return nlg

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['photo']
        
        payload = {"fashion_img": file}
        r = requests.post("http://127.0.0.1:7777/", files=payload).json()
        if r["status"] == "success":
            image_feature =  r["feature"]
        else:
            image_feature = []
    
        response = {
            "type": "greeting",
            "speaker": "system",
            "utterance": {
                "images": None,
                "false nlg": None,
                "nlg": "%s has received!"%str(image_feature)#file.name
            }
        }
        return json.dumps(response)

@app.route('/<path:path>')
def static_file(path):
    print "serving img file from",  path
    return send_file(path, mimetype='image/jpeg')

def load_state():
    with open(path.join(app.root_path, './history/status.json'), 'r') as f:
        return json.load(f)

def update_state(state, inter_child, leaf_node, attr_keywords, curr_id, detect_attr_dict):
    product_or_node_changed = False

    # update current node
    node_curr_round = leaf_node if leaf_node else None
    if not state['is_leaf_node'] and leaf_node != state['current_node']:
        state['current_node'] = node_curr_round
        product_or_node_changed = True
    if node_curr_round != None and state['current_node'] != leaf_node:
        state['current_node'] = node_curr_round
        product_or_node_changed = True

    # update curr_id
    def subset_attr(attr_dict, selected_attr):
        result = {}
        for attr in selected_attr:
            result[attr] = attr_dict[attr]
        return result

    if state['product_id'] == None and curr_id != None:
        product_or_node_changed = True
        state['product_id'] = curr_id.strip()
        product_attr_dict = get_attr_dict_by_id(state['product_id'], app.root_path)
        state['attr_dict'] = subset_attr(product_attr_dict, ['category'])

    if state['product_id'] and curr_id and state['product_id'] != curr_id:
        product_or_node_changed = True
        state['product_id'] = curr_id.strip()

    # update is_leaf_node
    if state['current_node']:
        state['is_leaf_node'] = True
    else:
        state['is_leaf_node'] = False

    # update missing and informed attr
    attr_names = ['genders', 'seasons', 'colors', 'materials', 'occasions', 'brand', 'necks', 'sleeves']

    if product_or_node_changed:
        missing, informed = [], []
        for k in attr_names:
            if k not in attr_keywords:
                missing.append(k)
            else:
                informed.append(k)
    else:
        missing, informed = state['missing_attr'], state['informed_attr']
        for k in attr_keywords:
            if k in missing:
                missing.remove(k)
                informed.append(k)
    state['missing_attr'] = missing
    state['informed_attr'] = informed

    # update attr_dict
    is_attribute_manipulation = False
    attr_dict = state['attr_dict']
    for k in detect_attr_dict:
        if k not in attr_dict:
            attr_dict[k] = detect_attr_dict[k]
            if k != 'category':
                is_attribute_manipulation = True
        elif attr_dict[k] != detect_attr_dict[k]:
            attr_dict[k] = detect_attr_dict[k]
            if k != 'category':
                is_attribute_manipulation = True


    # save to disk
    with open(path.join(app.root_path, './history/status.json'), 'w') as f:
        f.write(json.dumps(state))
    return state, is_attribute_manipulation

def clear_history():
    with open(path.join(app.root_path, './history/curr_history.json'), 'w') as output:
        history = """
        [
 {
  "type": "greeting", 
  "speaker": "user", 
  "utterance": {
   "images": null, 
   "false nlg": null, 
   "nlg": "Hello"
  }
 }, 
 {
  "type": "greeting", 
  "speaker": "system", 
  "utterance": {
   "images": null, 
   "false nlg": null, 
   "nlg": "Hi, how can i help you with something today?"
  }
 }]
        """
        output.write(history)



if __name__ == "__main__":
    # app.run(host='0.0.0.0')
    app.run()

