# process msmc
# To process msmc by population, user should prepare a population lst file
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

## individual bam file should be in the same folder with the bam file named by individual name, e.g.

## bam_folder
## |-- indv1_pop1.bam
## |-- indv2_pop1.bam
## |-- indv1_pop2.bam
## |-- indv2_pop2.bam


while read pop; do
    python msmc.py --sample-file $pop.lst --bam-folder bam_folder --out ./ --thread 8 --ref hg19
done < pops.lst
