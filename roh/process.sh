# process ROH
# To process ROH by population, user should prepare a population lst file
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


while read pop; do
    bcftools view -Oz -o $pop.vcf.gz -S $pop.lst MergedVariants.vcf.gz
    bcftools roh -G30 --AF-dflt 0.4 $pop.vcf.gz
done < pops.lst
