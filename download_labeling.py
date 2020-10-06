import glob
import io
import json
import re
import zipfile

import pandas as pd
import requests
from bs4 import BeautifulSoup


def download_files():
    data = pd.read_csv('NASID_clean_data.csv')

    out_dir = 'XML Files/'
    last_set_id = open('temp_file.txt', 'r').read()
    searching_set_id = True

    for i, SET_ID in enumerate(data['SET ID']):
        # skip all SET_ID up till last_set_id
        if last_set_id != '' and searching_set_id and SET_ID != last_set_id:
            continue
        searching_set_id = False

        # save current SET_ID to temp file
        open('temp_file.txt', 'w').write(SET_ID)

        # download ZIP file
        link = f'https://dailymed.nlm.nih.gov/dailymed/getFile.cfm?setid={SET_ID}&type=zip'

        try:
            r = requests.get(link)
            print(f'fetching file [{i + 1}]: {r.url}')
            z = zipfile.ZipFile(io.BytesIO(r.content))
        except Exception as e:
            print(e)
            open('skipped_files.txt', 'a').write(SET_ID + '\n')
            continue

        listOfFileNames = z.namelist()

        for fileName in listOfFileNames:
            # extract XML file ONLY
            if fileName.endswith('.xml'):
                z.extract(fileName, out_dir)

    # empty temp file when all XML files are downloaded
    open('temp_file.txt', 'w').write('')


def parse_xml(filename):
    file_content = open(filename, mode='r', encoding='utf-8').read()
    soup = BeautifulSoup(file_content, 'lxml')

    labelings = []

    codes = ['34066-1', '43685-7', '34084-4']
    for code in codes:
        content_items = soup.find(attrs={'code': code})

        if content_items is None:
            labelings.append({code: []})
            continue

        items = []

        content_items = content_items.parent.select('excerpt text list item')
        for content_item in content_items:
            match = re.findall('(.*)\\s*\\(', content_item.text)
            if len(match) > 0:
                items.append(match[0].strip())

        labelings.append({code: items})

    return labelings


def dump_to_json(json_data, filename):
    data = json.dumps(json_data)
    with open(filename, 'w') as f:
        f.write(data)


if __name__ == '__main__':
    xml_files = [f for f in glob.glob('XML Files/*.xml')]
    labels = []

    for i, xml_file in enumerate(xml_files):
        print(f'parsing file [{i}]: {xml_file}')

        parsed_items = parse_xml(xml_file)
        labels.append({xml_file: parsed_items})

    dump_to_json(labels, 'json_data.json')
