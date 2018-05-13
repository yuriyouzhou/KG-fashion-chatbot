from flask import Flask, render_template, request, send_from_directory, send_file
# from flask_uploads import UploadSet, configure_uploads, IMAGES
from predict import svm_intent, svm_response
from detect_attribute import detect_attribute
from locate_taxonomy import taxonomy_classify
from text_task_resnet.run_prediction import run_text_prediction
from get_img_by_id import get_img_by_id
import json
from os import path

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
    nodes = taxonomy_classify(msg, app.root_path)
    intersect_results, text_result = detect_attribute(msg, app.root_path)


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
        print text_result
        print "here", get_img_by_id(text_result, app.root_path)
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
    app.run()
