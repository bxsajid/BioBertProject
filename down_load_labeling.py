from urllib.request import urlretrieve
from zipfile import ZipFile

import pandas as pd

data = pd.read_csv('NASID_clean_data.csv')
SET_ID = data['SET ID']

url1 = 'https://dailymed.nlm.nih.gov/dailymed/getFile.cfm?setid='
url2 = '&type=zip'
outdir = 'XML Files'

for row in SET_ID:
    sky = row
    link = url1 + sky + url2
    name = outdir + sky + '.zip'
    urlretrieve(link, name)
    with ZipFile(name, 'r') as zipObj:
        # Get a list of all archived file names from the zip
        listOfFileNames = zipObj.namelist()
        # Iterate over the file names
        for fileName in listOfFileNames:
            # Check filename endswith csv
            if fileName.endswith('.xml'):
                # Extract a single file from zip
                zipObj.extract(fileName, outdir)
