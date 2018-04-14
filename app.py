from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, IMAGES
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import json
from os import path

app = Flask(__name__)
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")

# english_bot.set_trainer(ChatterBotCorpusTrainer)
# english_bot.train("chatterbot.corpus.english")

@app.route("/")
def home():
    global index
    index = 0
    return render_template("chat.html")

@app.route("/get")
def get_bot_response():
    msg = request.args.get('messageText')
    if "hi" in msg or "hello" in msg:
        clear_history()

    curr_turn = {
        "type": "greeting",
        "speaker": "user",
        "utterence": {
            "images": None,
            "false nlg": None,
            "nlg": msg
        }
    }

    end_response =  {
        "type": "greeting",
        "speaker": "system",
        "utterance": {
            "images": None,
            "false nlg": None,
            "nlg": "This conversation is over  :)"
        }
    }


    with open('./history/curr_history.txt') as data_file:
        old_data = json.load(data_file)
        if old_data is None:
            data = [curr_turn]
            index = 1
        else:
            data = old_data
            data.append(curr_turn)
            index = len(data)
            print("length of history", index)

    with open('./history/1.json') as answer:
        history = json.load(answer)
        try:
            if "user" in history[index]["speaker"]:
                index = index + 1

            response = [history[index ]]

            if index < len(history) and "system" in history[index + 1]["speaker"]:
                response.append(history[index + 1])
                print(index+1)
        except:
            return json.dumps([end_response])

        data.append(response)

        with open('./history/curr_history.txt', 'w') as outfile:
            outfile.write(json.dumps(data, outfile))

        # print(response)
        return json.dumps(response)




@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['photo']
        return json.dumps({'answer': "%s has received!"%file.name})


def clear_history():
    with open("./history/curr_history.txt", 'w') as output:
        output.write("null")

if __name__ == "__main__":
    app.run()
