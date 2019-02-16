import keras, json, os, time, numpy as np
from flask import Flask, jsonify, request, render_template
from keras.models import load_model 
from keras.preprocessing.sequence import pad_sequences
from keras import backend
backend.tensorflow_backend._get_available_gpus()

# Define application parameters
app = Flask('__web_app__')
models_folder = './models/'
data_folder = './data/'

# Load words and labels vocabularies
with open(data_folder+'ted_data_vocabs.json') as f:
    vocabs = json.load(f)

with open(data_folder+'ted_data_labels.json') as f:
    labels = json.load(f)

# Load pre-trained model on application start-up
print('Loading Model')
model = load_model('./models/ted_data_train_model.h5')
model._make_predict_function()
print('Model Loaded')

# Define custom functions
def process_input(text):
    '''
    Description: 
        - Tokenizes input text, converting it into integer sequence and pads it to defined maximum length

    Args:
        - text: Input text without punctuation
    
    Returns:
        - padded_text: Tokenized and padded text
    '''
    tokenized_text = []    
    tokenized_text.append([vocabs[word] for word in text.split()])
    padded_text = pad_sequences(tokenized_text, maxlen=128, padding='post', value=0)

    return padded_text

def make_prediction(processed_text):
    '''
    Description:
        - Makes punctuation prediction on input tokenized text, restores prediction back to plain text together with punctuation

    Args:
        - processed_text: Tokenized and padded text

    Returns:
        - restored_text: Punctuated input text
    '''
    words_seq = []
    for seq in processed_text:
        for word in seq:
            for value, index in vocabs.items():
                if word == index:
                    words_seq.append(value)

    prediction = model.predict(np.expand_dims(processed_text[0], axis=0))
    labels_seq = [np.argmax(word, axis=1) for word in prediction]

    restore_labels = []
    for labs in labels_seq:
        for lab in labs:
            for value, index in labels.items():
                if lab == index:
                    restore_labels.append(value)

    restored_text = []         
    for i in range(len(words_seq)):
        if restore_labels[i] == '<comma>':
            restored_text.append(str(words_seq[i])+',')
        elif restore_labels[i] == '<period>':
            restored_text.append(str(words_seq[i])+'.')
        elif restore_labels[i] == '<question>':
            restored_text.append(str(words_seq[i])+'?')
        elif restore_labels[i] == '<exclaim>':
            restored_text.append(str(words_seq[i])+'!')
        elif restore_labels[i] == '<3-dots>':
            restored_text.append(str(words_seq[i])+'...')
        else:
            restored_text.append(str(words_seq[i]))

    for i in range(len(restored_text)):
        if '.' in restored_text[i] or '?' in restored_text[i]:
            restored_text[i+1] = restored_text[i+1].capitalize()
        elif restored_text[i] == 'i':
            restored_text[i] = restored_text[i].capitalize()
        else:
            continue
   
    restored_text = ' '.join(restored_text)
    restored_text = restored_text.replace('<pad>', '')
    restored_text = restored_text[0].capitalize()+restored_text[1:].replace('ive', "I've")
    
    return restored_text

# Define Flask endpoints/routes
@app.route('/punct_text', methods=['POST'])
def punct_text():
    '''
    Description:
        - Flask endpoint to manage punctuation of input text by calling the required functions

    Returns:
        - Json result of punctuated text
    '''
    entered_text = request.form['entered_text']
    print('Making Predictions')
    start = time.time()
    processed_text = process_input(entered_text)
    predicted = make_prediction(processed_text)
    print('Completed. Time taken: {:.3f} seconds'.format(time.time()-start))

    return jsonify(result=predicted)

@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    Description: Flask endpoint to render index webpage
    '''
    return render_template('index.html')

# Start application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=False)