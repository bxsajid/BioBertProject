import csv
import json

from numpy import dot
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer

from helper.dump_to_json import dump_to_json


def read_meddra_terminology():
    meddra_terminology_filename = 'llt.csv'
    terminologies = []

    with open(meddra_terminology_filename, mode='r') as f:
        csv_data = csv.reader(f)
        for row in csv_data:
            terminologies.append(row[0])

    return terminologies


def find_meddra_terminology_in_labeling(meddra_terminologies):
    json_data_filename = 'log/fdalabel-query-111031/json_data.json'
    found_meddra_terms_filename = 'log/fdalabel-query-111031/found_meddra_terms.json'

    # load labeling from JSON
    with open(json_data_filename, mode='r') as f:
        filenames = json.load(f)

    # extract labels from JSON
    meddra_dict = {}
    for filename, labeling in filenames.items():
        sentence = ' '.join(labeling).replace('\\n', ' ').replace('\\t', ' ')

        found_meddra_terms = []
        for meddra_terminology in meddra_terminologies:
            if meddra_terminology in sentence:
                found_meddra_terms.append(meddra_terminology)

        meddra_dict[filename] = found_meddra_terms

    dump_to_json(meddra_dict, found_meddra_terms_filename, indent=True)


def find_mesh_similarity():
    found_meddra_terms_filename = 'log/fdalabel-query-111031/found_meddra_terms.json'

    # load MedDRA terms from JSON
    with open(found_meddra_terms_filename, mode='r') as f:
        filenames = json.load(f)

    # extract MedDRA terms from JSON
    terminologies_for_all_files = []
    for filename, labeling in filenames.items():
        print(f'in file, MedDRA count: {len(labeling)}')
        terminologies_for_all_files.append(set(labeling))

    common_terminologies = set()
    unique_terminologies = set()

    # find common and unique terminologies
    for terminologies_for_one_file in terminologies_for_all_files:
        common_terminologies = common_terminologies.intersection(terminologies_for_one_file)
        unique_terminologies = unique_terminologies.union(terminologies_for_one_file)

    common_terms_count = len(common_terminologies)
    unique_terms_count = len(unique_terminologies)
    jaccard_index = common_terms_count / unique_terms_count

    return {
        'common_terms_count': common_terms_count,
        'unique_terms_count': unique_terms_count,
        'jaccard_index': jaccard_index,
    }


def find_labeling_similarity():
    json_data_filename = 'log/fdalabel-query-111031/json_data.json'

    # load labeling from JSON
    with open(json_data_filename, mode='r') as f:
        filenames = json.load(f)

    # extract labels from JSON
    sentences = []
    for filename, labeling in filenames.items():
        sentence = ' '.join(labeling).replace('\\n', ' ').replace('\\t', ' ')
        sentences.append(sentence)

    model = SentenceTransformer('bert-base-nli-mean-tokens')
    sentence_embeddings = model.encode(sentences)

    # find cosine similarity
    a = sentence_embeddings[0]
    b = sentence_embeddings[1]
    cosine_similarity = float(dot(a, b) / (norm(a) * norm(b)))

    return {
        'cosine_similarity': cosine_similarity
    }


if __name__ == '__main__':
    # find Jaccard similarity
    meddra_terminologies = read_meddra_terminology()
    find_meddra_terminology_in_labeling(meddra_terminologies)
    mesh_similarity = find_mesh_similarity()

    # find Cosine similarity
    labeling_similarity = find_labeling_similarity()

    summary = {
        'mesh_similarity': mesh_similarity,
        'labeling_similarity': labeling_similarity
    }
    print(summary)

    # dump to json
    summary_filename = 'log/fdalabel-query-111031/summary_similarity.json'
    dump_to_json(summary, summary_filename, indent=True)
