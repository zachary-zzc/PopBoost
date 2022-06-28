import os
import sys
import subprocess
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter


chrs = ["chr{}".format(i) for i in range(1, 23)]


def arg_parser():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        conflict_handler="resolve", prog="msmc"
    )
    parser.add_argument(
        "--sample-file", required=True, dest="sample_file",
        metavar="STR", type=str,
        help="sample file with each sample as one line"
    )
    parser.add_argument(
        "--bam-folder", required=True, dest="bam_folder",
        metavar="STR", type=str,
        help="folder containing input bam format data, with bam named by sample.bam"
    )
    parser.add_argument(
        "--out", required=True, dest="outdir",
        metavar="STR", type=str,
        help="output msmc result"
    )
    parser.add_argument(
        "--mu", required=False, dest="mu",
        metavar="FLOAT", type=float, default=1.25e-8,
        help="mutation rate"
    )
    parser.add_argument(
        "--g", required=False, dest="g",
        metavar="FLOAT", type=float, default=8,
        help="years per generation"
    )
    parser.add_argument(
        "--shapeit-path", required=False, dest="shapeit",
        metavar="STR", type=str, default="shapeit",
        help="shapeit path"
    )
    parser.add_argument(
        "--samtools-path", required=False, dest="samtools",
        metavar="STR", type=str, default="samtoolse",
        help="samtools path"
    )
    parser.add_argument(
        "--ref", required=True, dest="ref",
        metavar="STR", type=str,
        help="reference path"
    )
    parser.add_argument(
        "--thread", required=False, dest="thread",
        metavar="INT", type=int, default=8,
        help="thread number"
    )
    return parser.parse_args()


def preprocess_msmc_command(bam, outdir, sample, ref, samtools):
    commands = []
    for ch in chrs:
        # step 1: calculate mean depth
        commands.append(
            "mean_depth=`samtools depth -r {} {} | awk '{sum += $3} END {print sum / NR}'`".format(
                ch, bam
            )
        )
        # step 2: generate vcf and mask file
        commands.append(
            "{} mpileup -q 20 -Q 20 -C 50 -u -r {} -f {} {} | bcftools call -c -V indels | ./bamCaller.py $mean_depth {}/{}.{}.mask.bed.gz | gzip -c > {}/{}.{}.vcf.gz".format(
                samtools, ch, ref, bam, outdir, sample, ch, outdir, sample, ch
            )
        )
        # step 3: run shapeit2, this will generate merged vcf named $outdir/$sample.phased.vcf.gz
        commands.append(
            "./run_shapeit.sh {}/{}.{}.vcf.gz {} {}".format(
                outdir, sample, ch, outdir, ch
            )
        )
    return commands

def generate_multihetsep(samples, outdir):
    commands = []
    # generate multi-het and mask by chromosome
    for ch in chrs:
        cmd = "./generate_multihetsep.py"
        cmd_mask = ""
        cmd_vcf  = ""
        for s in samples:
            cmd_mask += " --mask={}/{}.{}.mask.bed.gz".format(outdir, s, ch)
            cmd_vcf  += " {}/{}.{}.phased.vcf.gz".format(outdir, s, ch)
        cmd = cmd + cmd_mask + "--mask={}/mappability_mask.{}.bed.txt.gz".format(outdir, ch), cmd_vcf + " > {}/input.{}.multihetsep.txt".format(outdir, ch)
        commands.append(cmd)
    # merge all multi-het files by chromosome
    files = ""
    for ch in chrs:
        files += " {}/input.{}.multihetsep.txt".format(outdir, ch)
    commands.append("cat {} > {}/input.multihetsep.txt".format(files, outdir))
    return commends

def run_msmc(outdir, thread):
    commands = []
    # run msmc to estimate effective population size
    commands.append(
        "msmc2 -t {} -p 1*2+15*1+1*2 -o {}/output.msmc {}/input.multihetsep.txt".format(
            thread, outdir, outdir
        )
    )
    return commands

def main():
    args = arg_parser()
    with open("cmd.sh", "w") as ofs:
        with open(args.sample_file) as ifs:
            samples = [s.replace("\n", "") for s in ifs]
        # preprocess msmc command
        for s in samples:
            commands = preprocess_msmc_command(os.path.join(args.bam_folder, "{}.bam".format(s)),
                                               args.outdir,
                                               s,
                                               args.ref,
                                               args.samtools
                                               )
            for c in commands:
                ofs.write("{}\n".format(c))
        # generate_multihetsep
        commands = generate_multihetsep(samples, args.outdir)
        for c in commands:
            ofs.write("{}\n".format(c))
        # run msmc
        commands = run_msmc(args.outdir, args.thread)
        for c in commands:
            ofs.write("{}\n".format(c))
    # run cmd.sh
    out = subprocess.run("bash cmd.sh", shell=True, stdout=subprocess.PIPE)
    return out.stdout.decode("utf-8")


if __name__ == "__main__":
    main()

