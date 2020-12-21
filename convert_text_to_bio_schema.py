import gzip
import json


def read_file_content() -> str:
    description_filename = 'description/description.txt'
    with open(description_filename, mode='r') as f:
        return f.read()


def convert_text_to_token(txt: str) -> list:
    return txt.split(' ')


def read_mesh_dict() -> list:
    mesh_dict_filename = 'mesh.json.gz'
    with gzip.open(mesh_dict_filename, 'rb') as f:
        mesh_dict = json.load(f)

    return sorted(mesh_dict.items(), key=lambda t: t[1], reverse=True)


def map_mesh_terms_on_text(mesh_terms: list, txt: str):
    description_bio_schema_filename = 'description/description_bio_schema.tsv'

    with open(description_bio_schema_filename, mode='w') as f:
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
    text = read_file_content()
    # tokens = convert_text_to_token(text)
    mesh_pairs = read_mesh_dict()
    map_mesh_terms_on_text(mesh_pairs, text)

    # print(mesh_pairs)
