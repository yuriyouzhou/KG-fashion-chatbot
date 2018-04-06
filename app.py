from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, IMAGES
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import json
import os

app = Flask(__name__)
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")

# english_bot.set_trainer(ChatterBotCorpusTrainer)
# english_bot.train("chatterbot.corpus.english")


@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('messageText')

    answer = str(english_bot.get_response(userText))
    # score = 0.0
    # topic = 'shopping'

    wordCount = len(answer.split(" "))

    # return json.dumps({'answer': answer, 'score':score, 'topic': topic})
    return json.dumps( {
         "sentiment": {
          "label": ["anticipation", "Joy"],
          "anticipation": 0.941,
          "joy": 0.73,
          "trust": 0.59,
          "fear": 0.01,
          "surprise":0.042,
          "sadness":0.05,
          "disgust":0.03,
          "anger": 0.01,
         },
         "wordCount": wordCount
        })


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['photo']
        # file_name = photos.save(file)
        return json.dumps({'answer': "%s has received!"%file.name})



if __name__ == "__main__":
    app.run()
