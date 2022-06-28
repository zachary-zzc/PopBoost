# file format transform bed to diff
bed2diffs_v1 --bfile MergedVariants --nthreads 8

# run eems
runeems_snps --params eems.par

# plot result
## 1. the first parameter is the result directory
## 2. the second parameter is the plot directory
Rscript plotEEMS.R ./ plot
