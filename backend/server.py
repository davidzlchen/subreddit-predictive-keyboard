from flask import Flask, request, jsonify
from flask_cors import CORS

import character_lstm

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return 'Hello World!'

@app.route("/predict")
def predict():
    text = request.args.get('text')
    prediction = {'prediction': character_lstm.predict(text)}
    return jsonify(prediction)

if __name__ == "__main__":
    print("* Loading Keras model and Flask starting server...")
    character_lstm.init()
    app.run(threaded=True)
