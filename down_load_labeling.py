import io
import zipfile

import pandas as pd
import requests

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
