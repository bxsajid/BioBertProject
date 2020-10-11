import json

from helper.dump_to_json import dump_to_json

if __name__ == '__main__':
    mesh_ids_filename = 'mesh_ids.json'
    term_distribution_across_labeling_filename = 'output/term_distribution_across_labeling.json'
    term_count_across_labeling_filename = 'output/term_count_across_labeling.json'
    summary_filename = 'output/summary_filename.json'

    with open(mesh_ids_filename, mode='r') as f:
        content = json.load(f)

    term_distribution_across_labeling = {}
    term_count_across_labeling = {}
    total_terms = 0

    for filename, mesh_dict in content.items():
        term_count = len(mesh_dict)
        term_count_across_labeling[filename] = term_count
        total_terms += term_count

        for id, term in mesh_dict.items():
            if term not in term_distribution_across_labeling:
                term_distribution_across_labeling[term] = 1
            else:
                term_distribution_across_labeling[term] += 1

    # Question 1. What's distribution of MESH terms across the labeling?
    term_count_across_labeling = {k: v for k, v in sorted(term_count_across_labeling.items(), key=lambda item: item[1])}
    dump_to_json(term_count_across_labeling, term_count_across_labeling_filename)
    average_term_count = total_terms / len(content)

    # Question 2. What's top 10 MESH terms appeared across the labeling?
    term_distribution_across_labeling = {k: v for k, v in sorted(term_distribution_across_labeling.items(), key=lambda item: item[1], reverse=True)}
    dump_to_json(term_distribution_across_labeling, term_distribution_across_labeling_filename)

    # Summary of Question 1 and 2
    summary = {
        'term_across_labeling': {
            'minimum': list(term_count_across_labeling.values())[0],
            'maximum': list(term_count_across_labeling.values())[-1],
            'average': round(average_term_count),
        },
        'top_terms': list(term_distribution_across_labeling.keys())[:10]
    }
    dump_to_json(summary, summary_filename, indent=True)
