import os
import sys
import subprocess
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter


def arg_parser():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        conflict_handler="resolve", prog="phase"
    )
    parser.add_argument(
        "--mode", required=False, dest="mode",
        metavar="STR", type=str, default="low",
        help="low/normal coverage mode"
    )
    parser.add_argument(
        "--vcf", required=True, dest="vcf",
        metavar="STR", type=str,
        help="input vcf file"
    )
    parser.add_argument(
        "--out", required=True, dest="out",
        metavar="STR", type=str,
        help="output result"
    )


# ----- low coverage mode, process by angsd ---
def low_cov_pca(vcf, out):
    commands = []
    basename = vcf.replace(".vcf.gz", "").replace(".vcf", "")
    # step 1: get beagle likelihood
    commands.append(
        "vcftools --gzvcf {} --BEAGLE-PL --out {}".format(
            vcf, basename
        )
    )
    # step 2: run pcangsd
    commands.append(
        "python pcangsd.py -beagle {}.BEAGLE.PL -o {}".format(
            basename, out
        )
    )
    return commands


# ----- normal mode, process by smartPCA
def normal_pca(vcf, out):
    basename = vcf.replace(".vcf.gz", "").replace(".vcf", "")
    # step 1: convert vcf to eigen format, generate par file
    commands.append("plink --vcf {} --double-id --recode --out {}".format(vcf, basename))
    with open("convert.par", "w") as ofs:
        ofs.write("genotypename: {}.ped".format(basename))
        ofs.write("snpname: {}.map".format(basename))
        ofs.write("indivname: {}.ind".format(basename))
        ofs.write("outputformat: EIGENSTRAT")
        ofs.write("genotypeoutname: {}.geno".format(basename))
        ofs.write("snpoutname: {}.snp".format(basename))
        ofs.write("indivoutname: {}.ind".format(basename))
        ofs.write("familynames: NO")
    commands.append("convertf -p ped2eigenstrat.par")
    # step 2: run smartpca, generate par file
    with open("pca.par", "w") as ofs:
        ofs.write("genotypename: {}.geno".format(basename))
        ofs.write("snpname: {}.snp".format(basename))
        ofs.write("indivname: {}.ind".format(basename))
        ofs.write("evecoutname: {}.evec".format(out))
        ofs.write("evaloutname: {}.eval".format(out))
        ofs.write("altnormstyle: NO")
        ofs.write("numoutevec: 20")
        ofs.write("numoutlieriter: 5")
        ofs.write("outliersigmathresh: 6.0")
    commands.append("smartpca -p pca.par")
    return commands


def run_commands(commands):
    with open("run.sh", "w") as ofs:
        for c in commands:
            ofs.write("{}\n".format(c))
    out = subprocess.run("bash run.sh", shell=True, stdout=subprocess.PIPE)
    return out.stdout.decode("utf-8")


def main():
    args = arg_parser()
    if args.mode == "low":
        commands = low_cov_pca(args.vcf, args.out)
    elif args.mode == "normal":
        commands = normal_pca(args.vcf, args.out)
    run_commands(commands)


if __name__ == "__main__":
    main()
