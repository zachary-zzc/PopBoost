plink --vcf SiteEval/MergedVariants.vcf.gz --double-id --recode --out SiteEval/MergedVariants
convertf -p convert.par
smartpca -p pca.par
