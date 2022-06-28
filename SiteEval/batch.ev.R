library(genotypeeval)
library(TxDb.Hsapiens.UCSC.hg19.knownGene)
library(SNPlocs.Hsapiens.dbSNP142.GRCh37)

args <- commandArgs(T)
# 1 -- vcf file
# 2 -- output prefix
# 3 -- reference version

vcffn <- basename(args[1])
vcfpath <- paste0(dirname(args[1]), "/")

if (args[3] == "hg19") {
    vcf <- ReadVCFData(vcfpath, vcffn, "GRCh37")  # reference hg19
    suppressWarnings(library("TxDb.Hsapiens.UCSC.hg19.knownGene"))
    txdb <- TxDb.Hsapiens.UCSC.hg19.knownGene
    cds <- cds(txdb)
    seqlevelsStyle(cds) = "NCBI"
    genome(cds) <- "GRCh19"
    
    suppressWarnings(library("SNPlocs.Hsapiens.dbSNP144.GRCh37"))
    snps <- SNPlocs.Hsapiens.dbSNP144.GRCh37
} else if (args[3] == "hg38") {
    vcf <- ReadVCFData(vcfpath, vcffn, "GRCh38")  # reference hg38
    suppressWarnings(library("TxDb.Hsapiens.UCSC.hg38.knownGene"))
    txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene
    cds <- cds(txdb)
    seqlevelsStyle(cds) = "NCBI"
    genome(cds) <- "GRCh38"
    
    suppressWarnings(library("SNPlocs.Hsapiens.dbSNP141.GRCh38"))
    snps <- SNPlocs.Hsapiens.dbSNP141.GRCh38
} else {
    exit(1)
}


chrs <- c()
for (i in c(1:22)) {
    chr = paste0("ch", i)
    chrs <- c(chrs, chr)
}

dbsnp.all <- snplocs(snps, chrs, as.GRanges=TRUE)
seqlevelsStyle(dbsnp.all) = "NCBI"

gold.param = GoldDataParam(percent.confirmed=0.8)
if (args[3] == "hg19") {
    gold <- GoldDataFromGRanges("GRCh37", dbsnp.all, gold.param)
} else if (args[3] == "hg38") {
    gold <- GoldDataFromGRanges("GRCh38", dbsnp.all, gold.param)
} else {
    exit(1)
}
# skip admixture ref as the vcf contains samples from all over the world, 
# hard to say the components of each region (example file contain 5 british samples)

vcfparams <- VCFQAParam(count.limits=c(3e9, Inf))

ev.noref <- VCFEvaluate(vcf, vcfparams)
ev.ref   <- VCFEvaluate(vcf, vcfparams, gold.ref=gold, cds.ref=cds)

## results
outprefix <- args[2]

# without reference (no gold standard and no cds)
write.table(didSamplePass(ev.noref), paste0(outprefix, ".noref.res"), quote=F, row.name=F, sep="\t")
write.table(getResults(ev.noref), paste0(outprefix, ".noref.info.res"), quote=F, row.name=F, sep="\t")
pdf(paste0(outprefix, ".noref.pdf"))
getPlots(ev.noref)
dev.off()

# # with reference
write.table(didSamplePass(ev.ref), paste0(outprefix, ".ref.res"), quote=F, row.name=F, sep="\t")
write.table(getResults(ev.ref), paste0(outprefix, ".ref.info.res"), quote=F, row.name=F, sep="\t")
pdf(paste0(outprefix, ".ref.pdf"))
getPlots(ev.ref)
dev.off()
