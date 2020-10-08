import gzip
import json

mesh_ids_filename = 'mesh_ids.txt'
mesh_terms_filename = 'mesh_terms.txt'
mesh_dict_filename = 'mesh.json.gz'

# read mesh_dict file
with gzip.open(mesh_dict_filename, 'rb') as f:
    mesh_dict = json.load(f)

# read mesh_ids file
mesh_ids = sorted(set(mesh_id.strip() for mesh_id in open(mesh_ids_filename, mode='r').readlines()))

# create empty mesh_terms file
open(mesh_terms_filename, mode='w').write('')

# write mesh_terms to file
with open('mesh_terms.txt', mode='a') as f:
    for mesh_id in mesh_ids:
        print(mesh_id, mesh_dict[mesh_id])
        f.write(f'{mesh_dict[mesh_id]}\n')
