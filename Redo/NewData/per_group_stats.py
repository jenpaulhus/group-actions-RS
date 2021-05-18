# This script generates a file that can be uploaded to the 
#   hgcwa_per_group_stats db via the copy_from function

from lmfdb import db

def create_stats_file():
    '''
    Create the file per_group_stats.txt that can be uploaded to the 
    hgcwa_per_group_stats db via the copy_from function. To compute the data,
    the procedure queries the current hgcwa_genvectors db and uses the 
    completeness columns of the hgcwa_per_genus_stats db.
    '''
    f = open('scripts/higher_genus_w_automorphisms/per_group_stats.txt', 'w')
    cols = [['group','text'], ['genus','smallint'], ['g0_is_gt0','boolean'],
            ['g0_gt0_list','integer[]'], ['gen_vectors','integer'], 
            ['topological','integer'], ['braid','integer']]
    col_names = '|'.join([col[0] for col in cols]) + '\n'
    col_types = '|'.join([col[1] for col in cols]) + '\n'
    f.write(col_names)
    f.write(col_types)
    f.write('\n')
    data = compute_group_stats()
    for datum in data:
        line = '|'.join([str(val) for val in datum])
        f.write(line + '\n')
    f.close()

def compute_group_stats():
    '''
    Compute data for the hgcwa_per_group_stats db by querying the current
    hgcwa_genvectors db and using the completeness columns of the
    hgcwa_per_genus_stats db.
    '''
    data = []
    hgcwa = db.hgcwa_genvectors
    compdb = db.hgcwa_per_genus_stats
    genus_list = hgcwa.distinct('genus')
    for genus in genus_list:
        # rows for g0 = 0 table on unique groups page
        comp_info = compdb.lucky({'genus': genus},sort=[])
        group_stats_0 = hgcwa.count({'genus':genus, 'g0': 0}, ['group'])
        for group, gen_vectors in group_stats_0.items():        
            grp = group[0]
            labels = hgcwa.distinct(
                'label', {'genus':genus, 'g0': 0, 'group': grp})
            if comp_info['top_braid_compute']:
                topological = braid = 0
                for label in labels:
                    topological += len(hgcwa.distinct(
                        'topological', {'label': label}))
                    braid += len(hgcwa.distinct('braid', {'label': label}))
                data.append([grp, genus, "f", "\\N", gen_vectors, 
                             topological, braid])
            else:    
                data.append([grp, genus, "f", "\\N", gen_vectors, 
                             "\\N", "\\N"])
                
        # rows for g0 > 0 table on unique groups page
        if comp_info['g0_gt0_compute']:
            group_stats_gt0 = hgcwa.count(
                {'genus':genus, 'g0':{'$gt':0}}, ['group'])
            for group, gen_vectors in group_stats_gt0.items():
                grp = group[0]
                labels = hgcwa.distinct(
                    'label', {'genus':genus, 'g0':{'$gt':0}, 'group': grp})
                g0_list = print_list(hgcwa.distinct(
                          'g0', {'genus':genus, 'g0':{'$gt':0}, 'group': grp}))
                if comp_info['top_braid_g0_gt0']:
                    topological = braid = 0
                    for label in labels:
                        topological += len(hgcwa.distinct(
                            'topological', {'label': label}))
                        braid += len(hgcwa.distinct('braid', {'label': label}))
                    data.append([grp, genus, "t", g0_list, gen_vectors, 
                                 topological, braid])
                else:
                    data.append([grp, genus, "t", g0_list, gen_vectors,
                                 "\\N","\\N"])
    return data

def print_list(L):
    '''
    Convert the list L to a string surrounded by {} instead of [], as required
    by postgresql.
    '''
    strg = '{'
    for l in range(1,len(L)):
       strg = strg + str(L[l-1]) + ','
    strg = strg + str(L[len(L)-1])
    strg = strg + '}'
    return strg
