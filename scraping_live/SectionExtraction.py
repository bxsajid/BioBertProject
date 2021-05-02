import grpc
import os
import pandas as pd
import requests
import glob
import io
from bs4 import BeautifulSoup

from helper.dump_to_json import dump_to_json


def download_files():
    global base_dir

    data = pd.read('files')

    out_dir = 'files/'
    last_set_id = open(base_dir + 'temp_file.txt', 'r').read() if os.path.isfile(base_dir + 'temp_file.txt') else ''
    searching_set_id = True


def parse_xml(filename):
    global base_dir

    file_content = open(filename, mode='r', encoding='utf-8').read()
    soup = BeautifulSoup(file_content, 'lxml')
    text = []

    ids = ['.OVERVIEW', '.Introduction', '.Background', '.Hepatotoxicity']
    for id in ids:
        content_items = soup.find(attrs={'code': id})
        if content_items is None:
            continue

        text.append(content_items.parent.text.strip())

    return text


if __name__ == '__main__':
    global base_dir
    base_dir = 'C:\\Users\\bushr\\PycharmProjects\\practice\\files'

    # download XML files
    download_files()

    # download text in JSON format
    xml_files = [f for f in glob.glob('files/*.xml')]
    text = {}

    for i, xml_file in enumerate(xml_files):
        print(f'parsing file [{i}]: {xml_file}')
        text[xml_file] = parse_xml(xml_file)

    dump_to_json(text, base_dir + 'json_data.json', indent=False)
