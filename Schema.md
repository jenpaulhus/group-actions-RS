# Higher Genus Curves Database



## Main Table

`hgcwa_genvectors`: (OLD) Main data for the pages

Column            | Type     | Notes
------------------|----------|------
id                | bigint   |
ndim              |smallint  |  cut?
jacobian_decomp   | jsonb    |
cc                | jsonb    |  cut and replace with realcc?
realcc|integer[]|
full_auto|text|
passport_label|text|
group|text|
signH|text|
label|text|
hyp_involution|jsonb|
full_label|text|
eqn|jsonb|
cinv|jsonb|
hyperelliptic|boolean|
gen_vectors|jsonb|
total_label|text|
g0|smallint|
dim|smallint|
group_order|integer|
cyclic_trigonal|boolean|
r|smallint|
signature|text|  integer[]??
genus|smallint|
con|text|  may want to store conjugacy classes differently
braid|integer[]|
topological|integer[]|



`hgcwa_passports`: (OLD) Main data for the pages

Column            | Type     | Notes
------------------|----------|------
id                | bigint   |
ndim              |smallint  |
jacobian_decomp   | jsonb    |
cc                | jsonb    |
full_auto|text|
passport_label|text|
group|text|
signH|text|
label|text|
hyp_involution|jsonb|
full_label|text|
eqn|jsonb|
cinv|jsonb|
hyperelliptic|boolean|
gen_vectors|jsonb|
total_label|text|
g0|smallint|
dim|smallint|
group_order|integer|
cyclic_trigonal|boolean|
r|smallint|
signature|text|
genus|smallint|
con|text|
braid|integer[]|
topological|integer[]|
realcc|integer[]



## Statistics

`hgcwa_unique_groups`: Counts for the per genus list of groups

Column            | Type     | Notes
------------------|----------|------
group             | integer[]| GAP ID encoded as a pair of integers `[N,i]`, where `N` is the order of the group and `i` distinguishes groups of the same order (as determined in GAP or the gps_groups table)
genus             | smallint | genus
g0_is_gt0         | boolean  | whether the group is for quotient genus 0 or quotient genus >= 1
g0_gt0_list       | integer[]| list of g0 values this group appears for, if greater than 0
gen_vectors       | integer  | number of distinct generating vectors, up to simultaneous conjugation, for this genus and group
topological       | integer  | number of distinct generating vectors, up to topological equivalence, for this genus and group (if g0_is_gt0 is false)
braid             | integer  | number of distinct generating vectors, up to braid equivalence, for this genus and group (if g0_is_gt0 is false)

 



## Completeness Records

`hgcwa_complete`: for each genus, list if contains data for quotient genus >0  and whether braid and topological have been computed for that genus. Also totals for 
distinct families, refined passports, and generating vectors for statistics tables. 

Column            | Type     | Notes
------------------|----------|------
genus             | smallint | genus
g0_gt0_compute    | boolean  | whether quotient genus >0 data has been computed for this genus
top_braid_compute | boolean  | whether topological and braid equivalences have been computed for this genus and g0=0
top_braid_g0_gt0  | boolean  | False for now (whether topological and braid equivalences have been computed for g0>0)
num_families      | integer[]| 1st entry is number of distinct families for this genus total, nth entry is for quotient genus n-2
num_refined_pp    | integer[]| 1st entry is number of distinct refined passports for this genus, nth entry is for quotient genus n-2
num_gen_vectors   | integer[]| 1st entry is number of distinct generating vectors for this genus, nth entry is for quotient genus n-2
num_unique_groups | integer  | number of distinct groups of this genus 

