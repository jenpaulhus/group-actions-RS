# This program is an upload script for the hgcwa db

# Instructions:
# sage
# from hgcwa_data import main
# main(genus_list)
#    genus_list is a list of genera of the desired data


import json
import itertools
from sage.interfaces.magma import magma


def main(*genera):

  for genus in genera:

    print('Computing data for genus %d...' % genus)

    if genus < 10:
      genus_str = '0' + str(genus)
    else:
      genus_str = str(genus)

    # Temporary files
    supp_gxx = 'SupplementaryFiles/g%s' % genus_str
    possible_full = 'OutputFiles/g%spossible_full' % genus_str
    full = 'OutputFiles/g%sfull' % genus_str
    notfull = 'OutputFiles/g%snotfull' % genus_str
    tbldata = 'OutputFiles/TBLDATA'
    gxxfinaldata = 'g%sfinaldata' % genus_str

    # Make sure the temporary files are empty before running
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % supp_gxx)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % possible_full)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % full)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % notfull)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % tbldata)
    magma.eval('SetOutputFile("%s" : Overwrite:=true)' % gxxfinaldata)
    magma.eval('UnsetOutputFile()')

    # main.mag
    magma.load('genvectors.mag')
    magma.load('ries_helper_fn.mag')
    magma.set('g', genus)
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
    
    rf = open('g%sfinaldata' % genus_str, 'r')
    lines = rf.read().splitlines()
    rf.close()

    # Separate the list by the delimiter '@'
    grouped_lines = itertools.groupby(lines, lambda line : line == '@')
    entries = [list(entry) for is_delim, entry in grouped_lines if not is_delim]

    wf = open('g%s_hgcwa_data.txt' % genus_str, 'w')

    cols = [['genus','smallint'], ['total_label','text'], 
            ['passport_label','text'], ['label','text'], ['group','text'], 
            ['group_order','integer'], ['signature','integer[]'], 
            ['g0','smallint'], ['r','smallint'], ['dim','smallint'], 
            ['con','text'], ['cc','integer[]'], ['braid','integer[]'],
            ['topological','integer[]'], ['jacobian_decomp','jsonb'], 
            ['gen_vector','integer[]'], ['connected_genvec','text[]'], 
            ['hyperelliptic','boolean'], ['hyp_involution','integer'],
            ['eqn','jsonb'], ['cyclic_trigonal','boolean'], ['cinv','integer'], 
            ['full_label','text'], ['full_auto','text'], ['signH','text']]
    col_names = '|'.join([col[0] for col in cols]) + '\n'  
    col_types = '|'.join([col[1] for col in cols]) + '\n'
    wf.write(col_names)
    wf.write(col_types)
    wf.write('\n')
    
    for entry in entries:
      f_or_nf = entry[0]
      group = json.loads(entry[1])
      order = group[0]
      counter = group[1]
      group_str = '%d.%d' % (order, counter)
      signature = json.loads(entry[2])
      r = len(signature[1:])
      dim = r - 3
      #cc_classes = json.loads(entry[3])
      con = entry[4]
      cc = json.loads(entry[5])
      braid = entry[6]
      if braid == '[ 0, 0 ]':
        braid = 'NULL'
      topological = entry[7]
      if topological == '[ 0, 0 ]':
        topological = 'NULL'
      jacobian_decomp = entry[8]
      genvec = entry[9] # as a list of ranks
      connected_genvec = entry[11]
      if connected_genvec == 'Nonsolvable':
        connected_genvec = 'NULL'

      label = '%d.%d-%d.%d.%s' % (genus, order, counter, signature[0],
                                 '-'.join([str(num) for num in signature[1:]]))
      passport_label = '%s.%d' % (label, cc[0])
      total_label = '%s.%d' % (passport_label, cc[1])

      # line so far
      line = [str(genus), total_label, passport_label, label, group_str, str(order),
              str(signature), str(signature[0]), str(r), str(dim), con, str(cc), 
              braid, topological, jacobian_decomp, genvec, connected_genvec]

      if f_or_nf == 'F':
        hy_or_hn = entry[12]
        hyperelliptic = hy_or_hn == 'HY'
        if hyperelliptic:
          hyp_involution = entry[14]  # as rank
          eqn = entry[15]
          line.extend([str(hyperelliptic), hyp_involution, eqn])
        else:
          line.extend([str(hyperelliptic), 'NULL', 'NULL'])
        cy_or_cn = entry[16]
        cyclic_trigonal = cy_or_cn == "CY"
        if cyclic_trigonal:
          cinv = entry[18]  # as rank
          line.extend([str(cyclic_trigonal), cinv])
        else:
          line.extend([str(cyclic_trigonal), 'NULL'])
        # put NULL in full_label, full_auto, and signH
        line.extend(['NULL', 'NULL', 'NULL'])
      else: # not full automorphism group

        # put NULL in hyperelliptic, hyp_involution, eqn, cyclic_trigonal, and cinv
        line.extend(['NULL', 'NULL', 'NULL', 'NULL', 'NULL'])

        full_auto = json.loads(entry[12])
        signH = json.loads(entry[13])
        full_label = '%d.%d-%d.%d.%s' % (genus, full_auto[0], full_auto[1], signH[0],
                                        '-'.join([str(num) for num in signH[1:]]))
        line.extend([full_label, str(full_auto), str(signH)])
      
      # finally write the line
      output = '|'.join(line) + '\n'
      wf.write(output)

    # done iterating over data for the current genus
    wf.close()
    print('Done making upload file for genus %d' % genus)
  
  print('Done making all upload files')
