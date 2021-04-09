# To download data of a single genus
# run in lmfdb folder

from lmfdb import db

hg = db.hgcwa_passports



gendata = list(hg.search({'genus': 2}))
families = set()
for i in range(len(gendata)):
    families.add(gendata[i]['label'])

#Temporary DELETE
#family =u'2.5-1.0.5-5-5'

file = open('families_gen2.json'.format(0), 'a+')
 
file.write('load FILLNAME;' + '\n')
file.write('RecFormat:=recformat<group,signature,gen_vectors,cc>;'+ '\n')


for family in families:
    file.write('data:=[];' + '\n' +'\n')
    gp = hg.random({'label': family},projection='group')
    sig = hg.random({'label': family},projection='signature')
    file.write('gp_id:=')
    file.write(gp)
    file.write(';'+ '\n')
    
    file.write('signature:=')
    file.write(sig)
    file.write(';'+'\n'+'\n')

    file.write('g0:=signature[1];'+'\n')
    file.write('H:=SmallGroup(gp_id[1],gp_id[2]); n:=#H; LP:=[]; ')
    file.write('LG:=[g : g in H]; for i in [1..n] do x:=LG[i]; ')
    file.write('Tx:=[LG[j]*x : j in [1..n]]; permL:=[]; for j in [1..n] ')
    file.write('do for k in [1..n] do if Tx[j] eq LG[k] then permL[j]:=k; ')
    file.write('break; end if; end for; end for; Append(~LP,permL); end for; ')
    file.write('G:=PermutationGroup<n|LP>;'+'\n')
    file.write('S:=Sym(gp_id[1]);' + '\n')

    vectors = hg.search({'label': family},projection=['cc','gen_vectors'])
    for vect in vectors:
        file.write('gen_vectors:=')
        file.write('FILL GENS')
        file.write(';'+'\n')
        file.write('cc:=')
        file.write('FILLCCS')
        file.write(';'+'\n'+'\n')

        file.write('gen_vectors_as_perm:=[S!perm : perm in gen_vectors];'+'\n')
        file.write('Append(~data, rec<RecFormat |  gen_vectors:=gen_vectors_as_perm, cc:=cc>);'+'\n')
        
    file.write('FindOrbits(H,signature,data,g0);'+'\n'+'\n'+'\n')
   
file.close()

        
#vectors = hg.search({'label': family},projection=[
#    'label',
#    'cc',
#    'passport_label',
#    'total_label',
#    'gen_vectors',
#    'group',
#    'signature',
#    'genus'])

#for vect in vectors:
#    file = open('families_gen2.json', 'a')
#    file.write('['+str(vect)+']'+'\n')
#    file.close()

