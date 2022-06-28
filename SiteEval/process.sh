# merge vcf data
bcftools merge -0 -O z \
    -o MergedVariants.vcf.gz \
    tyc.filtered.vcf.gz sgdp.filtered.vcf.gz \
    tibetan.filtered.vcf.gz 1kg.filtered.vcf.gz

# get snp variants with only two alts
bcftools view -m2 -M2 -v snps -O z -o MergedVariants.snp.bi.vcf.gz \
    MergedVariants.vcf.gz
mv MergedVariants.snp.bi.vcf.gz MergedVariants.vcf.gz

# LD pruning
plink --vcf MergedVariants.vcf.gz --indep-pairwise 500 50 0.2 -out prune
plink --vcf MergedVariants.vcf.gz --extract prune.in --recode vcf --out MergedVaraints.prune.vcf

mv MergedVariants.prune.vcf MergedVariants.vcf && bgzip MergedVariants.vcf && tabix MergedVariants.vcf.gz

# Site annotation
perl annotate_variation.pl -downdb -webfrom annovar -buildver hg19 snp138 humandb/

# batch eval and site statistics
python get_vcf_stats.py --in MergedVariants.vcf.gz --out MergedVariants.statusV

# convert vcf data to plink bed format
plink --vcf MergedVariants.vcf.gz --make-bed --out MergedVariant

