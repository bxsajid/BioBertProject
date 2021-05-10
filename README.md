# BioBert Project

## Requirements

1. Please use focus on the attached labeling list for comparison, I highlighted the setid for your downloading in [csv file](fdalabel-query-111031.csv).
2. Use the MedDRA terminology instead of MESH terms. [Attached](llt.csv) please find the MedDRA terminology. You just use the exact match to extract MedDRA from labeling section (e.g., Boxed warnings, warning and precaution, and adverse reaction)
3. Then, use the Jaccard similarity to compare the labeling like you did.
4. Use sentence-based transformer package to do the comparison as you did last time.

## Working

### Phase 2

1. Run [download_labeling.py](download_labeling.py) to download XML files against setid in [csv file](fdalabel-query-111031.csv).
2. Run [check_similarity.py](check_similarity.py) to find Jaccard and Cosine similarity.

### Phase 3

Run [convert_text_to_bio_schema.py](convert_text_to_bio_schema.py) to convert [description/description.txt](description/description.txt) to BIO schema format saved in [description/description-bio-schema.tsv](description/description-bio-schema.tsv).

### Phase 4

1. Convert content of [json_data.json](json_data.json) to single long text and write to file [description/all-description.txt](description/all-description.txt).
2. Run [convert_text_to_bio_schema.py](convert_text_to_bio_schema.py) on content of [description/all-description.txt](description/all-description.txt) and output to [description/all-description-bio-schema.tsv](description/all-description-bio-schema.tsv).

### Phase 5

Run [find_unique_label.py](find_unique_label.py) to find unique labels like `B-D012306` from [description/all-description-bio-schema.tsv](description/all-description-bio-schema.tsv).

### Phase 6

Train NER classifier using SpaCy/BERT

- Split [description/all-description-bio-schema.tsv](description/all-description-bio-schema.tsv) into 60% [train](NER/data/train.tsv), 20% [validate](NER/data/devel.tsv) and
  20% [test](NER/data/train.tsv) data.
- Use [train.tsv](NER/data/train.tsv) and [devel.tsv](NER/data/devel.tsv) as input to train SpaCy/BERT model.
- Use [test.tsv](NER/data/test.tsv) to test the trained model.
- Run [NER/train_custom_ner_with_spacy.ipynb](NER/train_custom_ner_with_spacy.ipynb) to train the model.
- Run [NER/test_custom_ner_with_spacy.ipynb](NER/test_custom_ner_with_spacy.ipynb) to test the model.
- Alternatively
    - Run [NER/Spacy_NER.py](NER/Spacy_NER.py) to both train and test the model.

### [TODO]

- [x] Train classifier using SpaCy/BERT
    - To train NER classifier, use [description/all-description-bio-schema.tsv](description/all-description-bio-schema.tsv) as input to SpaCy/BERT.
- [ ] Train classifier using BioBERT
    - Use [description/unique_labels.json](description/unique_labels.json) in `get_labels()` method of `NerProcessor` class in [BioBERT code](https://github.com/dmis-lab/biobert/blob/master/run_ner.py).
    - To train NER classifier, split [description/all-description-bio-schema.tsv](description/all-description-bio-schema.tsv) into train/test and use as input to BioBERT.
