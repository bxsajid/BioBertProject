# https://www.youtube.com/watch?v=DxLcMI-EMYI
# https://aihub.cloud.google.com/p/products%2F2290fc65-0041-4c87-a898-0289f59aa8ba
import random
import time
import warnings
from itertools import chain
from os import path, mkdir

import numpy as np
import spacy
from spacy import displacy
from spacy.util import minibatch, compounding

if not path.isdir('data/'):
    mkdir('data/')
if not path.isdir('models/'):
    mkdir('models/')


def load_data_spacy(file_path):
    """ Converts data from:
    label \t word \n label \t word \n \n label \t word
    to: sentence, {entities : [(start, end, label), (start, end, label)]}
    """
    file = open(file_path, 'r')
    training_data, entities, sentence, unique_labels = [], [], [], []
    current_annotation = None
    start = end = 0  # initialize counter to keep track of start and end characters
    for line in file:
        line = line.strip('\n').split('\t')
        # lines with len > 1 are words
        if len(line) > 1:
            label = line[0][2:]  # the .txt is formatted: label \t word, label[0:2] = label_type
            label_type = line[0][0]  # beginning of annotations - "B", intermediate - "I"
            word = line[1]
            sentence.append(word)
            end += (len(word) + 1)  # length of the word + trailing space

            if label_type != 'I' and current_annotation:  # if at the end of an annotation
                entities.append((start, end - 2 - len(word), current_annotation))  # append the annotation
                current_annotation = None  # reset the annotation
            if label_type == 'B':  # if beginning new annotation
                start = end - len(word) - 1  # start annotation at beginning of word
                current_annotation = label  # append the word to the current annotation
            if label_type == 'I':  # if the annotation is multi-word
                current_annotation = label  # append the word

            if label != 'O' and label not in unique_labels:
                unique_labels.append(label)

        # lines with len == 1 are breaks between sentences
        if len(line) == 1:
            if current_annotation:
                entities.append((start, end - 1, current_annotation))
            sentence = ' '.join(sentence)
            training_data.append([sentence, {'entities': entities}])
            # reset the counters and temporary lists
            end = 0
            entities, sentence = [], []
            current_annotation = None
    file.close()
    return training_data, unique_labels


TRAIN_DATA, LABELS = load_data_spacy('data/train.txt')

# print([x[0] for x in TRAIN_DATA[1:10]])
# print([x[1] for x in TRAIN_DATA[1:10]])

warnings.filterwarnings('ignore')
nlp = spacy.load('en')
# nlp = spacy.load('en_core_web_sm')
TEST_DATA, _ = load_data_spacy('data/test.txt')

test_sentences = [x[0] for x in TEST_DATA[0:15]]  # extract the sentences from [sentence, entity]
for x in test_sentences:
    doc = nlp(x)
    displacy.render(doc, jupyter=True, style='ent')
warnings.filterwarnings('default')


# A simple decorator to log function processing time
def timer(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print("Completed in {} seconds".format(int(te - ts)))
        return result

    return timed


# Data must be of the form (sentence, {entities: [start, end, label]})
@timer
def train_spacy(train_data, labels, iterations, dropout=0.2, display_freq=1):
    """ Train a spacy NER model, which can be queried against with test data

    train_data : training data in the format of (sentence, {entities: [(start, end, label)]})
    labels : a list of unique annotations
    iterations : number of training iterations
    dropout : dropout proportion for training
    display_freq : number of epochs between logging losses to console
    """
    nlp = spacy.blank('en')
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)

    # Add entity labels to the NER pipeline
    for i in labels:
        ner.add_label(i)

    # Disable other pipelines in SpaCy to only train NER
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):
        nlp.vocab.vectors.name = 'spacy_model'  # without this, spaCy throws an "unnamed" error
        optimizer = nlp.begin_training()
        for itr in range(iterations):
            random.shuffle(train_data)  # shuffle the training data before each iteration
            losses = {}
            batches = minibatch(train_data, size=compounding(4., 32., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,
                    annotations,
                    drop=dropout,
                    sgd=optimizer,
                    losses=losses)
            if itr % display_freq == 0:
                print("Iteration {} Loss: {}".format(itr + 1, losses))
    return nlp


# Train (and save) the NER model
ner = train_spacy(TRAIN_DATA, LABELS, 6)
ner.to_disk("models/spacy_example")


def load_model(model_path):
    """ Loads a pre-trained model for prediction on new test sentences

    model_path : directory of model saved by spacy.to_disk
    """
    nlp = spacy.blank('en')
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)
    ner = nlp.from_disk(model_path)
    return ner


ner = load_model("models/spacy_example")

TEST_DATA, _ = load_data_spacy("data/test.txt")

test_sentences = [x[0] for x in TEST_DATA[0:15]]  # extract the sentences from [sentence, entity]
for x in test_sentences:
    doc = ner(x)
    displacy.render(doc, jupyter=True, style="ent")


def calc_precision(pred, true):
    precision = len([x for x in pred if x in true]) / (len(pred) + 1e-20)  # true positives / total pred
    return precision


def calc_recall(pred, true):
    recall = len([x for x in true if x in pred]) / (len(true) + 1e-20)  # true positives / total test
    return recall


def calc_f1(precision, recall):
    f1 = 2 * ((precision * recall) / (precision + recall + 1e-20))
    return f1


# run the predictions on each sentence in the test dataset, and return the spacy object
preds = [ner(x[0]) for x in TEST_DATA]

precisions, recalls, f1s = [], [], []

# iterate over predictions and test data and calculate precision, recall, and F1-score
for pred, true in zip(preds, TEST_DATA):
    true = [x[2] for x in list(chain.from_iterable(true[1].values()))]  # x[2] = annotation, true[1] = (start, end, annot)
    pred = [i.label_ for i in pred.ents]  # i.label_ = annotation label, pred.ents = list of annotations
    precision = calc_precision(true, pred)
    precisions.append(precision)
    recall = calc_recall(true, pred)
    recalls.append(recall)
    f1s.append(calc_f1(precision, recall))

print('Precision: {}\nRecall: {}\nF1-score: {}'.format(np.around(np.mean(precisions), 3),
                                                       np.around(np.mean(recalls), 3),
                                                       np.around(np.mean(f1s), 3)))
