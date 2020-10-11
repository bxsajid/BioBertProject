import gzip
import json
import os
import re
import traceback

import requests

from helper.append_to_json import append_to_json


def query_raw(text, url='https://bern.korea.ac.kr/plain'):
    return requests.post(url, data={'sample_text': text}).json()


if __name__ == '__main__':
    json_data_filename = 'json_data.json'
    description_filename = 'description/description.txt'
    description_next_index_filename = 'description_next_index.txt'
    description_skip_index_filename = 'description_skip_index.txt'
    mesh_ids_filename = 'mesh_ids.json'
    mesh_dict_filename = 'mesh.json.gz'

    # read labeling file
    with open(json_data_filename, mode='r') as f:
        descriptions = json.load(f)

    # read mesh_dict file
    with gzip.open(mesh_dict_filename, 'rb') as f:
        mesh_dict = json.load(f)

    # read next description index from file, if file exists
    start_filename, start_index = '', 0
    if os.path.isfile(description_next_index_filename):
        content = open(description_next_index_filename, mode='r').read()
        content_split = content.split(':')
        if len(content_split) == 2:
            start_filename, start_index = content_split
            start_index = int(start_index) if start_index.strip() and isinstance(int(start_index), int) else 0

    ERROR_COUNT_LIMIT = 3
    error_count = 0

    for filename, description in descriptions.items():
        print(filename)
        if start_filename and start_filename != filename:
            continue

        for i, description_list in enumerate(description):
            # write next description index to file
            open(description_next_index_filename, mode='w').write(f'{filename}:{i}')

            description_str = re.sub('\\s+', ' ', description_list)  # remove whitespace chars
            description_str = re.sub('"', '\'', description_str)  # replace " with '

            open(description_filename, mode='w', encoding='utf-8').write(description_str)
            filesize = os.stat(description_filename).st_size
            print(f'parsing description: {filename}, index: [{i} of {len(description)}], size: {(filesize / 1024):.2f} KB')

            try:
                response = query_raw(description)
            except Exception as e:
                traceback.print_exc()

                # keep record of descriptions which has error
                open(description_skip_index_filename, mode='a').write(f'{filename}:{i}\n')

                error_count += 1

                # stop script on ERROR_COUNT_LIMIT successive error response
                if error_count == ERROR_COUNT_LIMIT:
                    # remove temporary description file
                    if os.path.isfile(description_filename):
                        os.remove(description_filename)
                    break
                continue

            # reset error_count on success response
            error_count = 0

            mesh_id_term_dict = {}

            # extract MESH id from BERN server response
            for denotation in response['denotations']:
                for id in denotation['id']:
                    if id.startswith('MESH'):
                        mesh_id = id.lstrip('MESH:')
                        mesh_id_term_dict[mesh_id] = mesh_dict[mesh_id]

            append_to_json(filename, mesh_id_term_dict, mesh_ids_filename)

    # remove temporary description file
    if os.path.isfile(description_filename):
        os.remove(description_filename)
