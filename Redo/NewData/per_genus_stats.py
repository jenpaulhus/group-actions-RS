# This script generates a file that can be uploaded to the 
#   hgcwa_per_genus_stats db via the copy_from function

from lmfdb import db
import math

def create_stats_file():
    '''
    Create the file per_genus_stats.txt that can be uploaded to the 
    hgcwa_per_genus_stats db via the copy_from function. The procedure queries
    the current hgcwa_genvectors db to compute data for the stats columns of 
    of all the rows currently in the hgcwa_per_genus_stats db.
    '''
    f = open('scripts/higher_genus_w_automorphisms/per_genus_stats.txt', 'w')
    cols = [['genus','smallint'], ['g0_gt0_compute','boolean'], 
            ['top_braid_compute','boolean'], ['top_braid_g0_gt0','boolean'],
            ['nonabelian_only','boolean'], ['num_families','integer[]'], 
            ['num_refined_pp','integer[]'], ['num_gen_vectors','integer[]'], 
            ['num_unique_groups','integer']]
    col_names = '|'.join([col[0] for col in cols]) + '\n'
    col_types = '|'.join([col[1] for col in cols]) + '\n'
    f.write(col_names)
    f.write(col_types)
    f.write('\n')
    rows = compute_stats()
    for row in rows:
        line = '|'.join([wrangle(val) for val in row])
        f.write(line + '\n')
    f.close()

def compute_stats():
    '''
    Compute data for the stats columns of all the rows currently in the
    hgcwa_per_genus_stats db and return a list of updated rows.
    '''
    rows = []
    hgcwa = db.hgcwa_genvectors
    entries = db.hgcwa_per_genus_stats.search()
    for entry in entries:
        genus = entry['genus']
        # retrieve non-stats columns
        row = [genus, entry['g0_gt0_compute'], entry['top_braid_compute'], 
                      entry['top_braid_g0_gt0'], entry['nonabelian_only']]

        # Compute data for the columns num_families, num_refined_pp, 
        #   num_gen_vectors, and num_unique_groups
        # first entry is total number of distinct families, passports, or 
        #   gen_vectors for genus
        num_families = [len(hgcwa.distinct('label', {'genus':genus}))]
        num_refined_pp = [len(hgcwa.distinct(
                            'passport_label', {'genus':genus}))]
        num_gen_vectors = [hgcwa.count({'genus':genus})]

        num_unique_groups = len(hgcwa.distinct('group', {'genus':genus}))

        # second entry is number of distinct families, passports, or 
        #   gen_vectors for quotient genus 0
        num_families.append(len(hgcwa.distinct(
            'label', {'genus': genus, 'g0': 0})))
        num_refined_pp.append(len(hgcwa.distinct(
            'passport_label', {'genus': genus, 'g0': 0})))
        num_gen_vectors.append(hgcwa.count({'genus': genus, 'g0': 0}))

        if entry['g0_gt0_compute']:
            g0 = 1
            while g0 <= int(math.ceil(genus / 2)):
                # append counts for increasing quotient genus
                num_families.append(len(hgcwa.distinct(
                    'label', {'genus': genus, 'g0': g0})))
                num_refined_pp.append(len(hgcwa.distinct(
                    'passport_label', {'genus': genus, 'g0': g0})))
                num_gen_vectors.append(hgcwa.count({'genus': genus, 'g0': g0}))
                g0 += 1

        row.extend([num_families, num_refined_pp, 
                    num_gen_vectors, num_unique_groups])
        rows.append(row)
    
    return rows

def wrangle(val):
    '''
    Convert val to a string. If val is a list, then convert val to a string
    but put {} around it instead of [], as required by postgresql.
    '''
    if isinstance(val, list):
        return '{' + ', '.join([str(x) for x in val]) + '}'
    return str(val)
