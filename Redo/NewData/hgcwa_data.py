# This program generates a file that can be uploaded to the hgcwa db via
#   the copy_from function

# Command line instructions:
# sage
# from hgcwa_data import compute_data
# compute_data(genera [, mode])

# Examples: 
# compute_data([2,3,4,5])
# compute_data([5], 'nonabel')

import sys
import json
import itertools
from sage.interfaces.magma import magma

def compute_data(genera, mode='all'):
  '''
  Compute hgcwa data for the specified genera and output them in files that 
    can be uploaded to the hgcwa db via the copy_from function, called 
    gxx_all_data.txt, gxx_abel_data.txt, or gxx_nonabel_data.txt depending on
    the value of mode, where gxx refers to the specific genus.

  If mode='all' (the default), then all data will be computed for each genus. 
  If mode='abel', then only data for abelian groups will be computed
    for each genus.
  If mode='nonabel', then only data for nonabelian groups will be computed 
    for each genus.

  If db.gps_groups or db.gps_transitive have been updated recently, the scripts
    gps_decode.py and gps_transitive.py should be rerun to create new 
    gps_decode.mag and gps_transitive.mag files before running this procedure.

  Errors that occurred during computation are logged in errors.txt.
  '''
  # Check if arguments are valid
  try:
    for genus in genera:
      g = int(genus)
      if g < 2:
        raise ValueError
    if not(mode == 'all' or mode == 'abel' or mode == 'nonabel'):
      raise ValueError
  except:
    print('Invalid arguments')
    sys.exit(1)
  
  # Empty contents of errors.txt 
  magma.eval('SetOutputFile("%s" : Overwrite:=true)' % 'errors.txt')
  magma.eval('UnsetOutputFile()')
  magma.set('errorfile', '"%s"' % 'errors.txt')

  # Iterate over each genus
  for genus in genera:
    print('Computing data for genus %d...' % genus)

    genus_str = str(genus)
    if genus < 10:
      genus_str = '0' + genus_str

    # Names of temporary files created during computation
    supp_gxx = 'SupplementaryFiles/g%s' % genus_str
    possible_full = 'OutputFiles/g%spossible_full' % genus_str
    full = 'OutputFiles/g%sfull' % genus_str
    notfull = 'OutputFiles/g%snotfull' % genus_str
    tbldata = 'OutputFiles/TBLDATA'
    gxxfinaldata = 'g%sfinaldata' % genus_str

    # Make sure the temporary files are empty before beginning
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % supp_gxx)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % possible_full)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % full)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % notfull)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % tbldata)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % gxxfinaldata)
    magma.eval('UnsetOutputFile()')

    # Code adapted from main.mag
    magma.load('genvectors.mag')
    magma.load('ries_helper_fn.mag')
    magma.set('g', genus)
    magma.set('mode', '"%s"' % mode)
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
    if mode == 'abel':
      wf = open('g%s_abel_data.txt' % genus_str, 'w')
    elif mode == 'nonabel':
      wf = open('g%s_nonabel_data.txt' % genus_str, 'w')
    else:  # mode == 'all'
      wf = open('g%s_all_data.txt' % genus_str, 'w')
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
      con = entry[4]
      cc = json.loads(entry[5])
      braid = entry[6]
      if braid == '[ 0, 0 ]':
        braid = 'NULL'
      topological = entry[7]
      if topological == '[ 0, 0 ]':
        topological = 'NULL'
      jacobian_decomp = entry[8]
      genvec = entry[9]  # as a list of ranks
      connected_genvec = entry[11]
      if connected_genvec == 'Nonsolvable':
        connected_genvec = 'NULL'
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
      line = [str(genus), total_label, passport_label, label, group_str, 
              str(order), str(signature), str(g0), str(r), str(dim), con, 
              str(cc), braid, topological, jacobian_decomp, genvec, 
              connected_genvec, trans_group, min_deg]

      # The format of the entry is different depending on whether or not it 
      #   represents a full automorphism group
      if f_or_nf == 'F':  # full automorphism group
        hy_or_hn = entry[14]
        hyperelliptic = hy_or_hn == 'HY'
        if hyperelliptic:
          hyp_involution = entry[16]  # as a rank
          eqn = entry[17]
          line.extend([str(hyperelliptic), hyp_involution, eqn])
        else:
          line.extend([str(hyperelliptic), 'NULL', 'NULL'])
        cy_or_cn = entry[18]
        cyclic_trigonal = cy_or_cn == "CY"
        if cyclic_trigonal:
          cinv = entry[20]  # as a rank
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
        line.extend([full_label, full_auto_str, str(signH)])
      
      # Finally write the line
      output = '|'.join(line) + '\n'
      wf.write(output)

    # Finished iterating over the entries for the current genus
    wf.close()
    print('Done making upload file for genus %d' % genus)
  
  # Finished creating upload files for all the specified genera
  print('Done making all upload files')
