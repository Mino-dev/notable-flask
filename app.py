from flask import Flask,request,send_from_directory,render_template
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import tensorflow.compat.v1 as tf
tf.disable_eager_execution()
import cv2
import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
app = Flask(__name__, static_url_path='')

def sparse_tensor_to_strs(sparse_tensor):
    indices= sparse_tensor[0][0]
    values = sparse_tensor[0][1]
    dense_shape = sparse_tensor[0][2]
    strs = [ [] for i in range(dense_shape[0]) ]
    string = []
    ptr = 0
    b = 0
    for idx in range(len(indices)):
        if indices[idx][0] != b:
            strs[b] = string
            string = []
            b = indices[idx][0]
        string.append(values[ptr])
        ptr = ptr + 1
    strs[b] = string
    return strs


def normalize(image):
    return (255. - image)/255.


def resize(image, height):
    width = int(float(height * image.shape[1]) / image.shape[0])
    sample_img = cv2.resize(image, (width, height))
    return sample_img

voc_file = "vocabulary_semantic.txt"
model = "semantic_model/semantic_model.meta"

tf.reset_default_graph()
sess = tf.InteractiveSession()
# Read the dictionary
dict_file = open(voc_file,'r')
dict_list = dict_file.read().splitlines()
int2word = dict()
for word in dict_list:
    word_idx = len(int2word)
    int2word[word_idx] = word
dict_file.close()

# Restore weights
saver = tf.train.import_meta_graph(model)
saver.restore(sess,model[:-5])

graph = tf.get_default_graph()

input = graph.get_tensor_by_name("model_input:0")
seq_len = graph.get_tensor_by_name("seq_lengths:0")
rnn_keep_prob = graph.get_tensor_by_name("keep_prob:0")
height_tensor = graph.get_tensor_by_name("input_height:0")
width_reduction_tensor = graph.get_tensor_by_name("width_reduction:0")
logits = tf.get_collection("logits")[0]

# Constants that are saved inside the model itself
WIDTH_REDUCTION, HEIGHT = sess.run([width_reduction_tensor, height_tensor])

decoded, _ = tf.nn.ctc_greedy_decoder(logits, seq_len)

@app.route('/img/<filename>')
def send_img(filename):
    return send_from_directory('', filename)

@app.route("/")
def root():
    return render_template('index.html')

@app.route('/predict', methods = ['GET', 'POST'])
def predict():
    if request.method == 'POST':
        return render_template('result.html')
if __name__=="__main__":
    app.run()
