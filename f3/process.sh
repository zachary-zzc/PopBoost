# process f3
# To process f3 by population, user should prepare a population lst file
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


genotypename="MergedVariants.bed"
snpname="MergedVariants.bim"
indivname="MergedVariants.ind"

# ------------------ start to process admixture f3 --------------------
test="Mbuti"  # the test population should be specified by the user accordingly
popfilename="admix.f3.lst"
parfilename="admix.f3.par"

IFS=$'\n' read -d '' -r -a pops < pops.lst
length=${#pops[@]}

# generate pop file
for (( i=0; i<${length}; i++ )); do
    for (( j=${i}+1; j<${length}; j++ )); do
        echo "${pops[$i]}\t${pops[$j]}\t$test" >> $popfilename
    done
done
# generate par file
echo "genotypename: $genotypename" >> parfilename
echo "snpname: $snpname" >> parfilename
echo "indivname: $indivname" >> parfilename
echo "popfilename: $popfilename" >> parfilename
echo "outgroupmode: NO" >> parfilename
# run admixture f3 by qp
qp3Pop -p $parfilename

# ------------------ start to process outgroup f3 --------------------
outgroup="Mbuti"  # the outgroup population should be specified by the user accordingly
popfilename="outgroup.f3.lst"
parfilename="outgroup.f3.par"

IFS=$'\n' read -d '' -r -a pops < pops.lst
length=${#pops[@]}

# generate pop file
for (( i=0; i<${length}; i++ )); do
    for (( j=${i}+1; j<${length}; j++ )); do
        echo "${pops[$i]}\t${pops[$j]}\t$outgroup" >> $popfilename
    done
done
# generate par file
echo "genotypename: $genotypename" >> parfilename
echo "snpname: $snpname" >> parfilename
echo "indivname: $indivname" >> parfilename
echo "popfilename: $popfilename" >> parfilename
echo "outgroupmode: YES" >> parfilename
# run outgroupture f3 by qp
qp3Pop -p $parfilename
