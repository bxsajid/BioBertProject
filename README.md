# BioBert Project

## Requirements

1. Please use focus on the attached labeling list for comparison, I highlighted the setid for your downloading in [csv file](fdalabel-query-111031.csv).
2. Use the MedDRA terminology instead of MESH terms. [Attached](llt.csv) please find the MedDRA terminology. You just use the exact match to extract MedDRA from labeling section (e.g., Boxed warnings,
   warning and precaution, and adverse reaction)
3. Then, use the Jaccard similarity to compare the labeling like you did.
4. Use sentence-based transformer package to do the comparison as you did last time.

## Working

### Phase 2

1. Run `pyhton download_labeling.py` to download XML files against setid in `fdalabel-query-111031.csv`.
2. Run `python check_similarity.py` to find Jaccard and Cosine similarity.

### Phase 3

Run `convert_text_to_bio_schema.py` to convert `description/description.txt` to BIO schema format saved in `description/description-bio-schema.tsv`.

### [TODO]

1. Convert content of `json_data.json` to single long text and write to file `description/all-description.txt`.
2. Run `convert_text_to_bio_schema.py` on content of `description/all-description.txt` and output to `description/all-description-bio-schema.tsv`.