# This program generates a file that can be uploaded to the hgcwa_genvectors 
#   db via the copy_from function

# Examples: 
# compute_data([2,3,4,5])
# compute_data([5], groups='nonabel')

import json
import itertools
from sage.interfaces.magma import magma

def compute_data(genera, groups='all', g0_gt0_compute=True, 
                 top_braid_compute=True, top_braid_g0_gt0=False):
  '''
  Compute hgcwa data for the specified genera (list of integers) and output 
    the data in files that can be uploaded to the hgcwa db via the copy_from 
    function, called gxx_allgrps_data.txt, gxx_abelgrps_data.txt, or 
    gxx_nonabelgrps_data.txt depending on the value of groups, where gxx 
    refers to the specific genus.

  If groups='all', then data for all groups will be computed for each genus. 
  If groups='abel', then only data for abelian groups will be computed
    for each genus.
  If groups='nonabel', then only data for nonabelian groups will be computed 
    for each genus.

  The g0_gt0_compute parameter determines whether to compute g0>0 data for
    each genus.
  The top_braid_compute parameter determines whether to compute topological,
    braid equivalences for g0=0 and each genus.
  The top_braid_g0_gt0 parameter determines whether to compute topological,
    braid equivalences for g0>0 and each genus.
  
  The file gL_complete.txt, where L is the sequence of
    genera, will contain the completeness values, which can be uploaded to the
    hgcwa_per_genus_stats db.

  If db.gps_groups or db.gps_transitive have been updated recently, the scripts
    gps_decode.py and gps_transitive.py should be rerun to create new 
    gps_decode.mag and gps_transitive.mag files before running this procedure.

  The file log.txt will contain errors that occurred during computation and
    instances where a group not from db.gps_transitive is passed into RepEpi.
  '''
  # Check if arguments are valid
  try:
    for genus in genera:
      if genus < 2 or int(genus) != genus:
        raise ValueError
    if not(groups == 'all' or groups == 'abel' or groups == 'nonabel'):
      raise ValueError
    if not(type(g0_gt0_compute) == bool and type(top_braid_compute) == bool 
           and type(top_braid_g0_gt0) == bool):
      raise ValueError
    if top_braid_g0_gt0 and not g0_gt0_compute:
      raise ValueError
    if top_braid_g0_gt0:
      print('top,braid for g0>0 not implemented')
      raise ValueError
  except:
    print('Invalid arguments')
    return
  
  # Create a file that contains the completeness columns of the 
  #   hgcwa_per_genus_stats db but is missing the stats columns
  create_comp_file(genera, groups, g0_gt0_compute, 
                   top_braid_compute, top_braid_g0_gt0)
  
  # Empty contents of log.txt and TBLDATA
  magma.eval('SetOutputFile("%s" : Overwrite:=true)' % 'log.txt')
  magma.eval('SetOutputFile("%s" : Overwrite:=true)' % 'OutputFiles/TBLDATA')
  magma.eval('UnsetOutputFile()')
  magma.set('logfile', '"%s"' % 'log.txt')

  # Iterate over each genus
  for genus in genera:
    print('Computing data for genus %d...' % genus)

    genus_str = str(genus)
    if genus < 10:
      genus_str = '0' + genus_str

    # Names of temporary files for each genus
    supp_gxx = 'SupplementaryFiles/g%s' % genus_str
    possible_full = 'OutputFiles/g%spossible_full' % genus_str
    full = 'OutputFiles/g%sfull' % genus_str
    notfull = 'OutputFiles/g%snotfull' % genus_str
    gxxfinaldata = 'g%sfinaldata' % genus_str

    # Make sure the temporary files are empty before beginning
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % supp_gxx)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % possible_full)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % full)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % notfull)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % gxxfinaldata)
    magma.eval('UnsetOutputFile()')

    # Code adapted from main.mag
    magma.load('genvectors.mag')
    magma.load('ries_helper_fn.mag')
    magma.set('g', genus)
    magma.set('group_restriction', '"%s"' % groups)
    magma.set('g0_gt0_compute', '%s' % str(g0_gt0_compute).lower())
    magma.set('top_braid_compute', '%s' % str(top_braid_compute).lower())
    magma.set('top_braid_g0_gt0', '%s' % str(top_braid_g0_gt0).lower())
    magma.set('NotFullList', [])   
    magma.set('prtfile', '"%s"' % supp_gxx)
    magma.eval('SetColumns(0)')
    magma.load('SupplementaryFiles/BreuerRaw/g%s' % genus_str)
    magma.load('generate_ccnums.mag')
    magma.load(supp_gxx)
    magma.load(possible_full)
    magma.load('addl_data.mag')
    magma.load(full)
    magma.load(notfull)

    print('Done computing data for genus %d' % genus)
    print('Making upload file for genus %d...' % genus)
    
    # Read the temporary file containing the computed data so that we can
    #   create the upload file
    rf = open('g%sfinaldata' % genus_str, 'r')
    lines = rf.read().splitlines()
    rf.close()
    # Separate lines by the delimiter '@'
    grouped_lines = itertools.groupby(lines, lambda line : line == '@')
    entries = [list(entry) for is_delim, entry in grouped_lines if not is_delim]

    # Write column names and types to the upload file
    cols = [['genus','smallint'], ['total_label','text'], 
            ['passport_label','text'], ['label','text'], ['group','text'], 
            ['group_order','integer'], ['signature','integer[]'], 
            ['g0','smallint'], ['r','smallint'], ['dim','smallint'], 
            ['con','text[]'], ['cc','integer[]'], ['braid','integer[]'],
            ['topological','integer[]'], ['jacobian_decomp','jsonb'], 
            ['genvec','numeric[]'], ['connected_genvec','text[]'],
            ['trans_group','text'], ['min_deg','integer'],
            ['hyperelliptic','boolean'], ['hyp_involution','numeric'],
            ['eqn','text[]'], ['cyclic_trigonal','boolean'], ['cinv','numeric'], 
            ['full_label','text'], ['full_auto','text'], ['signH','integer[]']]
    col_names = '|'.join([col[0] for col in cols]) + '\n'  
    col_types = '|'.join([col[1] for col in cols]) + '\n'
    if groups == 'abel':
      wf = open('g%s_abelgrps_data.txt' % genus_str, 'w')
    elif groups == 'nonabel':
      wf = open('g%s_nonabelgrps_data.txt' % genus_str, 'w')
    else:  # groups == 'all'
      wf = open('g%s_allgrps_data.txt' % genus_str, 'w')
    wf.write(col_names)
    wf.write(col_types)
    wf.write('\n')
    
    # Iterate over each entry of the computed data
    for entry in entries:
      f_or_nf = entry[0]
      group = json.loads(entry[1])
      order = group[0]
      counter = group[1]
      group_str = '%d.%d' % (order, counter)
      signature = json.loads(entry[2])
      g0 = signature[0]
      r = len(signature[1:])
      dim = 3*g0 + r - 3
      con = put_curly_brackets(entry[4])
      cc = json.loads(entry[5])
      braid = json.loads(entry[6])
      if braid == [0,0]:
        braid = 'NULL'
      topological = json.loads(entry[7])
      if topological == [0,0]:
        topological = 'NULL'
      jacobian_decomp = entry[8]
      genvec = put_curly_brackets(entry[9])  # as a list of integers
      connected_genvec = entry[11]
      if connected_genvec == 'Nonsolvable':
        connected_genvec = 'NULL'
      else:
        connected_genvec = put_curly_brackets(connected_genvec)
      trans_group = entry[12]
      if trans_group == 'N/A':
        trans_group = 'NULL'
      min_deg = entry[13]
      if min_deg == 'N/A':
        min_deg = 'NULL'

      perm_orders = '0'
      if signature[1:] != []:  # cover is ramified
        perm_orders = '-'.join([str(perm_order) for perm_order in signature[1:]])

      label = '%d.%d-%d.%d.%s' % (genus, order, counter, g0, perm_orders)
      passport_label = '%s.%d' % (label, cc[0])
      total_label = '%s.%d' % (passport_label, cc[1])

      # Line of data so far
      line = [genus, total_label, passport_label, label, group_str, 
              order, signature, g0, r, dim, con, cc, braid, topological,
              jacobian_decomp, genvec, connected_genvec, trans_group, min_deg]
      line = list(map(convert_to_str, line))

      # The format of the entry is different depending on whether or not it 
      #   represents a full automorphism group
      if f_or_nf == 'F':  # full automorphism group
        hy_or_hn = entry[14]
        hyperelliptic = hy_or_hn == 'HY'
        if hyperelliptic:
          hyp_involution = entry[16]  # as an integer
          eqn = put_curly_brackets(entry[17])
          line.extend([str(hyperelliptic), hyp_involution, eqn])
        else:
          line.extend([str(hyperelliptic), 'NULL', 'NULL'])
        cy_or_cn = entry[18]
        cyclic_trigonal = cy_or_cn == "CY"
        if cyclic_trigonal:
          cinv = entry[20]  # as an integer
          line.extend([str(cyclic_trigonal), cinv])
        else:
          line.extend([str(cyclic_trigonal), 'NULL'])
        # put NULL for full_label, full_auto, signH
        line.extend(['NULL', 'NULL', 'NULL'])
      else:  # not a full automorphism group
        # put NULL for hyperelliptic, hyp_involution, eqn, cyclic_trigonal, cinv
        line.extend(['NULL', 'NULL', 'NULL', 'NULL', 'NULL'])

        full_auto = json.loads(entry[14])
        full_auto_str = '%d.%d' % (full_auto[0], full_auto[1])
        signH = json.loads(entry[15])

        perm_ordersH = '0'
        if signH[1:] != []:  # cover is ramified
          perm_ordersH = '-'.join([str(perm_order) for perm_order in signH[1:]])
        full_label = '%d.%d-%d.%d.%s' % (genus, full_auto[0], full_auto[1], 
                                         signH[0], perm_ordersH)
        line.extend([full_label, full_auto_str, convert_to_str(signH)])
      
      # Finally write the line
      output = '|'.join(line) + '\n'
      wf.write(output)

    # Finished iterating over the entries for the current genus
    wf.close()
    print('Done making upload file for genus %d' % genus)
  
  # Finished creating upload files for all the specified genera
  print('Done making all upload files')


def create_comp_file(genera, groups, g0_gt0_compute,
                     top_braid_compute, top_braid_g0_gt0):
  '''
  Create the file gL_complete.txt that can be uploaded to the 
  hgcwa_per_genus_stats db via the copy_from function. The file will only
  contain values for the completeness columns and will be missing
  data for the stats columns. 
  '''
  print('Making completeness file...')
  cols = [['genus','smallint'], ['g0_gt0_compute','boolean'], 
          ['top_braid_compute','boolean'], ['top_braid_g0_gt0','boolean'],
          ['nonabelian_only','boolean'], ['num_families','integer[]'], 
          ['num_refined_pp','integer[]'], ['num_gen_vectors','integer[]'], 
          ['num_unique_groups','integer']]
  col_names = '|'.join([col[0] for col in cols]) + '\n'
  col_types = '|'.join([col[1] for col in cols]) + '\n'
  genera.sort()
  g_ls_str = ','.join([str(g) for g in genera])
  f = open('g%scomplete.txt' % g_ls_str, 'w')
  f.write(col_names)
  f.write(col_types)
  f.write('\n')
  nonabelian_only = groups == 'nonabel'
  for genus in genera:
    row = [str(genus), str(g0_gt0_compute), str(top_braid_compute), 
           str(top_braid_g0_gt0), str(nonabelian_only), 
           'NULL', 'NULL', 'NULL', 'NULL']
    line = '|'.join(row)
    f.write(line + '\n')
  f.close()
  print('Done making completeness file')


def convert_to_str(val):
  '''
  Convert val to a string. If val is a list, put {} around val
  instead of [], as required by postgresql.
  '''
  if isinstance(val, list):
    return put_curly_brackets(str(val))
  return str(val)


def put_curly_brackets(ls_str):
  '''
  Replace the [] with {} around ls_str, a string representation of a
  list surrounded by [].
  '''
  return '{' + ls_str[1:-1] + '}'
