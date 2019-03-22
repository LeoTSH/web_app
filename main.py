import keras, json, os, time, numpy as np
from flask import Flask, jsonify, request, render_template
from keras.models import load_model 
from keras.preprocessing.sequence import pad_sequences
from keras import backend
backend.tensorflow_backend._get_available_gpus()

# Define Flask parameters
app = Flask('__web_app__')

# Define models and data folders
data_folder = './data/'
models_folder = './models/'

# Load words and labels vocabularies
with open(data_folder+'ted_data_vocabs.json') as f:
    vocabs = json.load(f)

with open(data_folder+'ted_data_labels.json') as f:
    labels = json.load(f)

# Load pre-trained model on Flask start-up
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
    # Create list to store tokenized sentence
    tokenized_text = []    
    # Append tokenized sentence to list
    tokenized_text.append([vocabs[word] for word in text.split()])
    # Pad tokenized sentence to max sentence length of 128
    padded_text = pad_sequences(tokenized_text, maxlen=128, padding='post', value=0)

    # Return padded sentence
    return padded_text

def get_key(dic, val):
    '''
    Description:
        - Returns key from dictionary based on value
    
    Args:
        - dic: Dictionary of either labels or vocabularies
        - val: Value of key-value pair in dictionary
    
    Returns:
        - key: Dictionary key based on value
    '''
    # Iterate dictionary
    for key, value in dic.items():
        if value == val:
            return key

def make_prediction(processed_text):
    '''
    Description:
        - Makes punctuation prediction on input tokenized text, restores prediction back to plain text together with punctuation

    Args:
        - processed_text: Tokenized and padded text

    Returns:
        - restored_text: Punctuated input text
    '''
    # Create list to store original sentence
    words_seq = []
    # Iterate tokenized text, extract corresponding text and append it to list
    for seq in processed_text:
        for word in seq:
            words_seq.append(get_key(vocabs, word))

    # Make prediction on tokenized sentence
    prediction = model.predict(np.expand_dims(processed_text[0], axis=0))
    # Extracted predicted labels from one-hot encoding
    labels_seq = [np.argmax(word, axis=1) for word in prediction]

    # Create list to store restored predicted labels
    restore_labels = []
    # Iterate through extracted labels, extract corresponding label text and append it to list
    for labs in labels_seq:
        for lab in labs:
            restore_labels.append(get_key(labels, lab))

    # Create list to store punctuated sentence
    restored_text = []         
    # Iterate thorugh original sentence and merge with predicted labels text
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

    # Capitalize first word in a sentence and 'I'
    for i in range(len(restored_text)):
        if '.' in restored_text[i] or '?' in restored_text[i]:
            restored_text[i+1] = restored_text[i+1].capitalize()
        elif restored_text[i] == 'i':
            restored_text[i] = restored_text[i].capitalize()
        else:
            continue

    # Join sentence from list
    restored_text = ' '.join(restored_text)
    # Remove <pad> tokens
    restored_text = restored_text.replace('<pad>', '')
    restored_text = restored_text[0].capitalize()+restored_text[1:].replace('ive', "I've")
    
    # Return restored sentence
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
    # Extract entered sentence from submitted form data
    entered_text = request.form['entered_text']
    print('Making Predictions')
    start = time.time()
    try:
        # Tokenize sentence
        processed_text = process_input(entered_text)
        # Make predictions on tokenized sentence
        predicted = make_prediction(processed_text)
        print('Completed. Time taken: {:.3f} seconds'.format(time.time()-start))

        # Return jsonified restored sentence
        return jsonify(result=predicted)
    except:
        return jsonify(error='Sentence error, please kindly re-check')
    
@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    Description: Flask endpoint to render index webpage
    '''

    # Display default page
    return render_template('index.html')

# Start Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=False)