from flask import Flask, render_template, request, send_from_directory, send_file
# from flask_uploads import UploadSet, configure_uploads, IMAGES
from predict import svm_intent, svm_response
from detect_attribute import detect_attribute
from locate_taxonomy import taxonomy_classify
from text_task_resnet.run_prediction import run_text_prediction
from get_img_by_id import get_img_by_id
import json
from os import path
import csv
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

    inter_child, leaf_node, leaf_sample_img_ID = taxonomy_classify(msg, app.root_path)
    detect_attr_dict, intersect_result, text_retrieval_rest = detect_attribute(msg, app.root_path)

    state = load_state()
    state = update_state(state, inter_child, leaf_node, detect_attr_dict, leaf_sample_img_ID)

    if state['is_leaf_node']:
        if not detect_attr_dict:
            # no attribute detected, give representative response
            response = [{
                "intent_type": intent_type,
                "response_type": response_type,
                "speaker": "system",
                "utterance": {
                    "images": [get_img_by_id(leaf_sample_img_ID, app.root_path)],
                    "false nlg": None,
                    "nlg": "check this %s out! you can ask more about %s" % (leaf_node[0], ', '.join(state['missing_attr']))
                }
            }]
            return json.dumps(response)
        elif state['product_id']:
            # a product is located
            nlg = get_info_by_id(state['product_id'], state['missing_attr'])
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
                attr_names = ['gender', 'season', 'color', 'material', 'occasion', 'brand', 'neck',
                              'sleeve', 'category']

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
        msg = "Which one do you like? %s"% ', '.join(inter_child)
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


def get_info_by_id(id, attr):
    with open(path.join(app.root_path, 'attribute_detection', 'attributes_65572.txt'), 'r') as f:
        attributes = json.loads(f.readline())
        for item in attributes['products']:
            if id == item['ID']:
                out = [item['ID'], item['brand'], item['price'],
                       item['genders'], item['colors'], item['materials'],
                       item['occasions'], item['necks'], item['sleeves'],
                       item['texts'], item['category']]
            return ' '.join(out)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['photo']
        response = {
            "type": "greeting",
            "speaker": "system",
            "utterance": {
                "images": None,
                "false nlg": None,
                "nlg": "%s has received!"%file.name
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

def update_state(state, inter_child, leaf_node, detect_attr_dict, curr_id):
    product_or_node_changed = False
    # update current node
    node_curr_round = leaf_node if leaf_node else None
    if not state['is_leaf_node'] and leaf_node != state['current_node']:
        state['current_node'] = node_curr_round
        product_or_node_changed = True

    # update curr_id

    if state['product_id'] == None and curr_id != None:
        product_or_node_changed = True
        state['product_id'] = curr_id.strip()

    if state['product_id'] and curr_id and state['product_id'] != curr_id:
        product_or_node_changed = True
        state['product_id'] = curr_id.strip()

    # update is_leaf_node
    if state['current_node']:
        state['is_leaf_node'] = True
    else:
        state['is_leaf_node'] = False

    # update missing and informed attr
    attr_names = ['gender', 'season', 'color', 'material', 'occasion', 'brand', 'neck',
                  'sleeve', 'category']

    if product_or_node_changed:
        missing, informed = [], []
        for k in attr_names:
            if k not in detect_attr_dict:
                missing.append(k)
            else:
                informed.append(k)
    else:
        missing, informed = state['missing_attr'], state['informed_attr']
        for k in detect_attr_dict:
            if k in missing:
                missing.remove(k)
                informed.append(k)
    state['missing_attr'] = missing
    state['informed_attr'] = informed



    # save to disk
    with open(path.join(app.root_path, './history/status.json'), 'w') as f:
        f.write(json.dumps(state))
    return state

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

