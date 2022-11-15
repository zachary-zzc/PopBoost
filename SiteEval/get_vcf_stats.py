import os
import sys
import subprocess
import vcf
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter


def arg_parser():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        conflict_handler="resolve", prog="get_vcf_stats"
    )
    parser.add_argument(
        "--in", required=True, dest="infile",
        metavar="STR", type=str,
        help="input vcf format data"
    )
    parser.add_argument(
        "--out", required=True, dest="outprefix",
        metavar="STR", type=str,
        help="output prefix"
    )
    parser.add_argument(
        "--ref", required=False, dest="ref",
        metavar="STR", type=str, default="hg19",
        help="reference version, hg19 or hg38"
    )
    return parser.parse_args()


# ----- aux functions for calculation statistics -----
def is_ti(ref, alt):
    cand = sorted([ref.upper(), alt.upper()])
    if cand == ["A", "G"] or cand == ["C", "T"]:
        return True
    return False

def is_tv(ref, alt):
    if not is_ti(ref, alt):
        return True
    return False

def is_dbsnp(record):
    name = record.ID
    if name is not None and name.startswith('rs'):
        return True
    return False
# ----- aux functions done ----


# ----- batch eval by Rscript -----
def batch_eval(infile, outprefix, refv):
    cmd = "Rscript batch.ev.R {} {} {}".format(infile, outprefix, refv)
    print(cmd)
    out = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    return out.stdout.decode("utf-8")
# ----- batch eval done -----


def cal_stat(infile, outprefix):
    reader = vcf.Reader(filename=infile)
    # output logs
    # ti loci
    ti_loci = {}
    # tv loci
    tv_loci = {}
    # annotated in dbsnp, should be annotated vcf by annovar
    dbsnp_loci = {}
    non_dbsnp_loci = {}
    # total snp count
    count = 0
    valid_count = 0

    cur_chrom = ""
    for record in reader:
        count += 1
        # record should have only one alt (bi alelle)
        if len(record.ALT) != 1:
            print(record)
            print(record.ALT, record.is_snp)
            continue
        valid_count += 1
        if record.CHROM != cur_chrom:
            # init cur chromosome
            ti_loci[record.CHROM] = 0
            tv_loci[record.CHROM] = 0
            dbsnp_loci[record.CHROM] = 0
            non_dbsnp_loci[record.CHROM] = 0
            cur_chrom = record.CHROM
        # process ti/tv
        if is_ti(record.REF, record.ALT[0].sequence):
            ti_loci[cur_chrom] += 1
        elif is_tv(record.REF, record.ALT[0].sequence):
            tv_loci[cur_chrom] += 1
        # process exist database (dbsnp only)
        if is_dbsnp(record):
            dbsnp_loci[cur_chrom] += 1
        else:
            non_dbsnp_loci[cur_chrom] += 1

    # save records
    # import pickle as pkl
    # pkl.dump(ti_loci, open(f"{outprefix}.ti.sites.pkl", "wb"))
    # pkl.dump(tv_loci, open(f"{outprefix}.tv.sites.pkl", "wb"))
    # pkl.dump(dbsnp_loci, open(f"{outprefix}.dbsnp.sites.pkl", "wb"))
    # pkl.dump(non_dbsnp_loci, open(f"{outprefix}.nondbsnp.sites.pkl", "wb"))

    with open(f"{outprefix}.out", "w") as ofs:
        ti_count = sum([c for c in ti_loci.values()])
        tv_count = sum([c for c in tv_loci.values()])
        dbsnp_count = sum([c for c in dbsnp_loci.values()])
        uniq_count = sum([c for c in non_dbsnp_loci.values()])
        print(f"Total number of variants in the vcf file: {count}")
        print(f"Total number of valid variants (bi-allele snvs): {valid_count}")
        print(f"Number of ti sites: {ti_count}")
        print(f"Number of tv sites: {tv_count}")
        print("Calculated TI/TV ratio: {}".format(float(ti_count) / float(tv_count)))
        print(f"Number of uniq called sites: {uniq_count}")
        print(f"Number of called sites shared with dbsnp: {dbsnp_count}")
        print("Ratio of population uniq sites: {}".format(float(uniq_count) / float(count)))

        ofs.write(f"Total number of variants in the vcf file: {count}\n")
        ofs.write(f"Total number of valid variants (bi-allele snvs): {valid_count}\n")
        ofs.write(f"Number of ti sites: {ti_count}\n")
        ofs.write(f"Number of tv sites: {tv_count}\n")
        ofs.write("Calculated TI/TV ratio: {}\n".format(float(ti_count) / float(tv_count)))
        ofs.write(f"Number of uniq called sites: {uniq_count}\n")
        ofs.write(f"Number of called sites shared with dbsnp: {dbsnp_count}\n")
        ofs.write("Ratio of population uniq sites: {}\n".format(float(uniq_count) / float(count)))


def main():
    args = arg_parser()
    batch_eval(args.infile, args.outprefix, args.ref)
    cal_stat(args.infile, args.outprefix)


if __name__ == "__main__":
    main()
