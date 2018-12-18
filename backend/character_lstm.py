import numpy as np
import tensorflow as tf
from keras.models import Sequential, load_model
from keras.layers import LSTM
from keras.layers import Dense, Activation
from keras.backend import get_session
from keras.optimizers import RMSprop
import json
import heapq

SEQUENCE_LENGTH = 40
NUM_CHARS = 217

CHAR_INDICES_FP = 'char_indices.json'
INDICES_CHAR_FP = 'indices_char.json'
MODEL_WEIGHT_FP = 'reddit_test.h5'

def init():
    global model, graph, char_indices, indices_char

    get_session().run(tf.global_variables_initializer())

    model = create_model()
    model.load_weights(MODEL_WEIGHT_FP)

    graph = tf.get_default_graph()

    char_indices = {}
    with open(CHAR_INDICES_FP, 'r') as fp:
        char_indices = json.load(fp)

    indices_char = {}
    with open(INDICES_CHAR_FP, 'r') as fp:
        indices_char = json.load(fp)

def create_model():
    model = Sequential()
    model.add(LSTM(128, input_shape=(SEQUENCE_LENGTH, NUM_CHARS)))
    model.add(Dense(NUM_CHARS))
    model.add(Activation('softmax'))
    return model

def prepare_input(text):
    x = np.zeros((1, SEQUENCE_LENGTH, NUM_CHARS))
    for t, char in enumerate(text):
        x[0, t, char_indices[char]] = 1.
    return x

def sample(preds, top_n=3):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds)
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    return heapq.nlargest(top_n, range(len(preds)), preds.take)

def predict_completion(text):
    original_text = text
    generated = text
    completion = ''
    spaces = 0
    while True:
        x = prepare_input(text)
        with graph.as_default():
            preds = model.predict(x, verbose=0)[0]
        next_index = sample(preds, top_n=1)[0]
        next_char = indices_char[str(next_index)]
        text = text[1:] + next_char
        completion += next_char
        if len(original_text + completion) + 2 > len(original_text) and next_char == ' ':
            return completion

def predict_completions(text, n=3):
    x = prepare_input(text)
    with graph.as_default():
        preds = model.predict(x, verbose=0)[0]
    next_indices = sample(preds, n)
    return [indices_char[str(idx)] + predict_completion(text[1:]
        + indices_char[str(idx)]) for idx in next_indices]

def padding(phrase):
    if len(phrase) < 40:
        thing = ''
        thing += ' ' * (40-len(phrase))
        thing += phrase
        return thing
    else:
        return phrase

def predict(text):
    seq = padding(text).lower()
    seq = seq[len(seq) - 40: len(seq)]
    return predict_completions(seq, 5)

