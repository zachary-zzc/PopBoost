# run phase script

python phase.py --mode low \
    --vcf MergedVariants.vcf.gz \
    --out MergedVariants.phased.vcf.gz \
    --thread 8 --burn 10 --prune 10
    --shapeit-path <shapeit2 program path>
    --beagle-path <beagle java file path>
