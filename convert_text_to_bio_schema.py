import gzip
import json
import re


def convert_json_to_text_file() -> None:
    json_data_filename = 'json_data.json'
    description_filename = 'description/all-description.txt'

    # load labeling from JSON
    with open(json_data_filename, mode='r', encoding='utf-8') as f:
        filenames = json.load(f)

    # extract labels from JSON
    sentences = []
    for filename, labeling in filenames.items():
        sentence = ' '.join(labeling).replace('\\n', ' ').replace('\\t', ' ')
        sentences.append(sentence)

    # replace multiple spaces with single space
    sentences = re.sub('\\s+', ' ', ' '.join(sentences))

    # write description to file
    with open(description_filename, mode='w', encoding='utf-8') as f:
        f.write(sentences)


def read_file_content() -> str:
    description_filename = 'description/all-description.txt'
    with open(description_filename, mode='r', encoding='utf-8') as f:
        return f.read()


def convert_text_to_token(txt: str) -> list:
    return txt.split(' ')


def read_mesh_dict() -> list:
    mesh_dict_filename = 'mesh.json.gz'
    with gzip.open(mesh_dict_filename, 'rb') as f:
        mesh_dict = json.load(f)

    return sorted(mesh_dict.items(), key=lambda t: t[1], reverse=True)


def map_mesh_terms_on_text(mesh_terms: list, txt: str):
    description_bio_schema_filename = 'description/all-description-bio-schema.tsv'

    with open(description_bio_schema_filename, mode='w', encoding='utf-8') as f:
        while not (txt is None):
            term_found = False

            for mesh_term_key, mesh_term_value in mesh_terms:
                if txt.startswith(mesh_term_value):
                    mesh_term_value_tokens = mesh_term_value.split(' ')

                    for i, mesh_term_value_token in enumerate(mesh_term_value_tokens):
                        if i == 0:
                            f.write(f'{mesh_term_value_token}\tB-{mesh_term_key}\n')
                        else:
                            f.write(f'{mesh_term_value_token}\tI-{mesh_term_key}\n')

                    pieces = txt.split(mesh_term_value, 1)

                    term_found = True
                    print(mesh_term_value)
                    break

            if not term_found:
                pieces = txt.split(' ', 1)
                word = pieces[0]
                f.write(f'{word}\tO\n')
                print(word)

            # update txt with remaining content and continue search for MESH terms
            txt = pieces[1].lstrip() if len(pieces) > 1 else None


if __name__ == '__main__':
    convert_json_to_text_file()
    text = read_file_content()
    # tokens = convert_text_to_token(text)
    mesh_pairs = read_mesh_dict()
    map_mesh_terms_on_text(mesh_pairs, text)

    # print(mesh_pairs)
