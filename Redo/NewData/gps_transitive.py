from lmfdb import db

# Instructions:
# sage
# from scripts.higher_genus_w_automorphisms.gps_transitive import create_list
# create_list()

# create_list writes the list gps_transitive to a magma file.
# Each element of gps_transitive is [gapidfull, n, gens], representing a 
#   transitive subgroup of Sn of minimal n isomorphic to gapidfull
# For solvable groups, this permutation subgroup is passed into RepEpi
def create_list():
    f = open('scripts/higher_genus_w_automorphisms/gps_transitive.mag', 'w')
    gapidfull_list = db.gps_transitive.distinct('gapidfull')
    output_str = 'gps_transitive := [ '
    for gapidfull in gapidfull_list:
        min_n = db.gps_transitive.min('n', {'gapidfull':gapidfull})
        min_iter = db.gps_transitive.search({'gapidfull':gapidfull, 'n':min_n})
        min_entry = next(min_iter)
        gens_str = ''
        for perm in min_entry['gens']:
            formatted_perm = [f'({str(p)[1:-1]})' for p in perm]
            formatted_perm = ''.join(formatted_perm)
            formatted_perm = f'\"{formatted_perm}\"'
            gens_str = gens_str + formatted_perm + ', '
        gens_str = '[' + gens_str[:-2] + ']'
        group_label = '.'.join(gapidfull[1:-1].split(','))
        group_label = f'\"{group_label}\"'
        data_str = ', '.join([group_label, str(min_n), gens_str])
        output_str += f'[* {data_str} *],\n'
    output_str = output_str[:-2] + ' ];'
    f.write(output_str)
    f.close()
