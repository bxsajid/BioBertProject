import json

from numpy import dot
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer

from helper.dump_to_json import dump_to_json


def find_mesh_similarity():
    handcrafted_mesh_id_filename = 'input/handcrafted_mesh_id.json'

    # load MESH ids from JSON
    with open(handcrafted_mesh_id_filename, mode='r') as f:
        filenames = json.load(f)

    # extract MESH ids from JSON
    labels = []
    for filename, labeling in filenames.items():
        print(f'in file, mesh id count: {len(labeling)}')
        labels.append(labeling)

    # find common MESH ids
    common_mesh_id_count = 0
    for label in labels[0]:
        if label in labels[1]:
            common_mesh_id_count += 1

    unique_mesh_id_count = len(set(labels[0] + labels[1]))
    jaccard_index = common_mesh_id_count / unique_mesh_id_count

    return {
        'unique_mesh_id_count': unique_mesh_id_count,
        'common_mesh_id_count': common_mesh_id_count,
        'jaccard_index': jaccard_index,
    }


def find_labeling_similarity():
    handcrafted_labeling_filename = 'input/handcrafted_labeling.json'

    # load labeling from JSON
    with open(handcrafted_labeling_filename, mode='r') as f:
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
    mesh_similarity = find_mesh_similarity()
    labeling_similarity = find_labeling_similarity()

    summary = {
        'mesh_similarity': mesh_similarity,
        'labeling_similarity': labeling_similarity
    }
    print(summary)

    # dump to json
    summary_filename = 'output/summary_similarity.json'
    dump_to_json(summary, summary_filename, indent=True)
