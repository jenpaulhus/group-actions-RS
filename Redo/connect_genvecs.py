import re
import json
from lmfdb import db

# Instructions:
# sage
# from scripts.higher_genus_w_automorphisms.connect_genvecs import process_connections
# process_connections(g)
#   g is the genus of the data


# regex patterns for the generators returned by magma
identity_str = r'Id\(G\)'
identity = re.compile(identity_str)

base_str = r'G.(-?[0-9]+)'
base = re.compile(base_str)

power_str = r'\^(-?[0-9]+)'
power = re.compile(power_str)

conjugate_str = fr'\^{base_str}'
conjugate = re.compile(conjugate_str)


# Helper function for process_connections
# gen_str is the current generator string, and genvec
#    is the current generating vector
def processGen(gen_str, genvec):
    parts = gen_str.split(sep=" * ")
    letters = []
    for p in parts:
        # p is either of the form G.i, G.i^j, G.i^G.j, or Id(G)
        m = identity.match(p)
        if m is not None:
            letters.append('Id(G)')
        else:
            m = base.match(p)
            i = m.group(1)
            letter = chr(int(i)+96)
            remaining = p[len(m.group(0)):]
            if remaining == '':
                letters.append(letter)
            else:
                m = power.match(remaining)
                if m is not None:
                    j = m.group(1)
                    letters.append(f'{letter}^{j}')
                else:
                    m = conjugate.match(remaining)
                    j = m.group(1)
                    letter2 = chr(int(j)+96)
                    letters.append(f'{letter}^{letter2}')
    # reverse letters so that evaluating from right to left gives
    # the correct permutation
    letters.reverse() 
    # put the letters next to each other
    gen = ''.join(letters)
    genvec.append(gen)


# Convert connected generating vectors to the presentations of
#    generators on the abstract groups pages, which use letters a,b,c,...
def process_connections(genus):
    if genus < 10:
        genus_str = '0' + str(genus)
    else:
        genus_str = str(genus)
    input_file = f'scripts/higher_genus_w_automorphisms/g{genus_str}_connected_genvecs.json'
    output_file = f'scripts/higher_genus_w_automorphisms/g{genus_str}_processed_genvecs.txt'
    with open(input_file) as f:
        data = json.load(f)
        wf = open(output_file, 'x')
        wf.write('passport_label|connected_gen_vectors\ntext|jsonb\n\n')
        for pair in data:
            passport_label = pair[0]
            connected_genvec = pair[1]
            genvec = []

            group_label = passport_label.split('.')[1]
            o_c = group_label.split('-')
            order = o_c[0]
            counter = o_c[1]
            group = db.gps_groups.lookup(f'{order}.{counter}')

            # Process the connected genvecs to get them in the correct format
            if group['solvable']:
                for gen_str in connected_genvec:
                    processGen(gen_str, genvec)
            else:
                genvec = connected_genvec.reverse()

            line = '|'.join([passport_label, str(genvec)])
            wf.write(line + '\n')
        wf.close()
                