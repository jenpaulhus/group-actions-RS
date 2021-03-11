from lmfdb import db
from lmfdb.groups.abstract.web_groups import WebAbstractGroup

# Instructions:
# sage
# from scripts.higher_genus_w_automorphisms.gps_decode import create_list
# create_list()

# Note that the gps_groups database is sorted by order, then counter.
# create_list writes the list gps_decode to a magma file.
# Each element of gps_decode is 
#    [label, pc_code, ngens, gens_used, -elt_rep_type, perm_gens],
#    representing a group in the groups db.
# If a group is solvable, then perm_gens is the string "solvable"
# Otherwise, the group is unsolvable:
#    -elt_rep_type is the degree of the permutation representation and 
#       perm_gens is a list of generators
#    if an exception occurred when trying to get perm_gens,
#       perm_gens is the string "error"
def create_list():
    f = open('scripts/higher_genus_w_automorphisms/gps_decode.mag', 'x')
    gps_db = db.gps_groups
    gps_iter = gps_db.search()
    output_str = 'gps_decode := [ '
    for gp in gps_iter:
        label = gp['label']
        label_str = f'\"{label}\"'
        data_str = ', '.join([label_str, str(gp['pc_code']), str(gp['ngens']),
                              str(gp['gens_used']), str(-gp['elt_rep_type'])])
        if gp['solvable'] == True:
            data_str += ', \"solvable\"'
        else:
            group = WebAbstractGroup(gp['label'])
            perm_gens = []
            try:
                for code in gp['perm_gens']:
                    perm_gens.append(f'\"{group.decode_as_perm(code)}\"')
                perm_gens_str = '[' + ', '.join(perm_gens) + ']'
            except:
                data_str += ', \"error\"'
            else:
                data_str += ', ' + perm_gens_str
        output_str += f'[* {data_str} *],\n'
    output_str = output_str[:-2] + ' ];'
    f.write(output_str)
    f.close()
