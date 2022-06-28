# process fst
# To process fst by population, user should prepare a population lst file
# with each population in one line, named "pops.lst".
# For each population, user should prepare an individual lst
# with each individual in one line. The file name should be named by the population name.

## Example for "pops.lst"
## -----------------------
## pop1
## pop2

## Example for individual files
## pop1.lst
## -----------------------
## indv1_pop1
## indv2_pop1

## pop2.lst
## -----------------------
## indv1_pop2
## indv2_pop2


IFS=$'\n' read -d '' -r -a pops < pops.lst
length=${#pops[@]}

# pairwise process populations
for (( i=0; i<${length}; i++ )); do
    for (( j=${i}+1; j<${length}; j++ )); do
        vcftools --gzvcf MergedVariants.vcf.gz --weir-fst-pop ${pops[$i]}.lst --weir-fst-pop ${pops[$j]}.lst
    done
done
