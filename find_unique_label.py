from typing import List
import json


def read_bio_file() -> List[str]:
    description_bio_schema_filename = 'description/all-description-bio-schema.tsv'

    with open(description_bio_schema_filename, mode='r', encoding='utf-8') as f:
        return f.readlines()


def find_unique_label(bio_contents: List[str]) -> List:
    unique_labels = set()

    for i, bio_content in enumerate(bio_contents):
        content = bio_content.strip()
        if content == '':
            continue

        label = content.split('\t')[1] if '\t' in content else content
        unique_labels.add(label)

    return list(unique_labels)


def save_label_to_file(unique_labels: List[str]) -> None:
    unique_labels_filename = 'description/unique_labels.json'

    with open(unique_labels_filename, mode='w', encoding='utf-8') as f:
        json.dump(unique_labels, f, indent=None)


if __name__ == '__main__':
    contents = read_bio_file()
    labels = find_unique_label(contents)
    save_label_to_file(labels)

    print(list(labels))
    print(len(labels))
