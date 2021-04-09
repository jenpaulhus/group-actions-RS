# BELOW IS CODE I HANDRAN
#change 2 to larger g

from lmfdb import db
import yaml
import sys

hgcwa = db.hgcwa_passports

file_name = "genus77.yaml"
output_file = open(file_name, 'r')
gen_vectors = yaml.load(output_file.read(),Loader=yaml.FullLoader)
for genvec_id in gen_vectors:
    genvec = gen_vectors[genvec_id]
    braid_id = genvec['braid']
    top_id = genvec['topological']
    # Get the cc of the representatives
    braid_cc = list(hgcwa.search({'id': braid_id}))[0]['cc']
    top_cc = list(hgcwa.search({'id': top_id}))[0]['cc']
    hgcwa.upsert({'id': genvec_id}, {'braid': braid_cc, 'topological': top_cc})



     #print(braid_cc,top_cc,genvec_id)
    # Update the database one generating vector at a time
    #DOESNT WORK SINCE genvec_id is not id!!!
