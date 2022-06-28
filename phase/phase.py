import os
import sys
import subprocess
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter


# global params
## genetic map is used in high coverage mode
## user should set this to their own path
genemap = "genetic_map.txt"


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
        help="input vcf data"
    )
    parser.add_argument(
        "--out", required=True, dest="out",
        metavar="STR", type=str,
        help="output phased vcf data"
    )
    parser.add_argument(
        "--thread", required=False, dest="thread",
        metavar="INT", type=int, default=1,
        help="thread number for running beagle/shapeit2"
    )
    parser.add_argument(
        "--burn", required=False, dest="burn",
        metavar="INT", type=int, default=10,
        help="burn interation number for running phase"
    )
    parser.add_argument(
        "--prune", required=False, dest="prune",
        metavar="INT", type=int, default=10,
        help="prune iteration number for running phase"
    )
    parser.add_argument(
        "--shapeit-path", required=False, dest="shapeit",
        metavar="STR", type=STR, default="shapeit",
        help="system shapeit path"
    )
    parser.add_argument(
        "--beagle-path", required=False, dest="beagle",
        metavar="STR", type=STR, default="beagle.jar",
        help="system beagle jar file path"
    )
    return parser.parse_args()


# ----- process in low coverage mode -----
def phase_low_cov(vcf, out, thread, burn, prune, beagle, shapeit):
    commands = []
    # step1: define beagle chunks
    commands.append(
        "makeBGLCHUNKS --vcf {} --window 700 --overlap 200 --output chunk.coordinates".format(
        vcf
        )
    )
    # step2: Run beagle 4
    commands.append(
        "while read line; do\n"
        "    chr=$(echo $line | awk '{ print $1 }')\n"
        "    from=$(echo $line | awk '{ print $2 }')\n"
        "    to=$(echo $line | awk '{ print $3 }')\n"
        "    ivcf={}\n"
        "    ovcf=output.beagle4.$chr\.$from\.$to\n"
        "    java -Xmx4g -jar {} gl=$ivcf out=$ovcf chrom=$chr\:$from\-$to\n"
        "done < chunk.coordinates".format(
            vcf, beagle
        )
    )
    # step3: convert beagle output to shapeit2 input
    commands.append(
        """prepareGenFromBeagle4 --likelihoods {} \
            --posteriors output.beagle4.*.vcf.gz \
            --threshold 0.995 \
            --output input.shapeit""".format(
                vcf
            )
    )
    # step4: run shapeit2
    commands.append(
        """{} -call\
        --input-gen input.shapeit.gen.gz input.shapeit.gen.sample\
        --input-init input.shapeit.hap.gz input.shapeit.hap.sample\
        --input-map map.txt.gz\
        --input-scaffold scaffold.haps.gz scaffold.haps.sample\
        --input-thr 1.0\
        --thread {}\
        --burn {}\
        --run 12\
        --prune {}\
        --output-max output.shapeit.haps.gz output.shapeit.haps.sample\
        --output-log output.shapeit.log\
        """.format(shapeit, thread, burn, prune)
    )
    # step5: Ligate SHAPEIT chunks
    commands.append(
        """ligateHAPLOTYPES --vcf {}\
                 --scaffold scaffolded_samples.txt\
                 --chunks output.chunk1.hap.gz output.chunk1.hap.gz output.chunk1.hap.gz\
                 --output output.ligated.hap.gz""".format(
                    vcf
                 )
    )
    # format transform, from hap data to vcf
    commands.append(
        "{} -convert --input-haps output.ligated.hap.gz --output-vcf {}".format(
            shapeit, out
        )
    )
    return commands


# ----- process in high coverage mode -----
def phase_normal_cov(vcf, out, burn, prune, thread, shapeit):
    # step1: phase
    commands.append(
        "{} --input-vcf {} -M {} -O output.hap.gz --burn {} --prune {} --thread {}".format(
            shapeit, vcf, genemap, burn, prune, thread
        )
    )
    # step2: format convert
    commands.append(
        "{} -convert --input-haps output.hap.gz --output-vcf {}".format(
            shapeit, out
        )
    )
    return commands


# ----- aux functions -----
def run_commands(commands):
    with open("run.sh", "w") as ofs:
        for c in commands:
            ofs.write("{}\n".format(c))
    out = subprocess.run("bash run.sh", shell=True, stdout=subprocess.PIPE)
    return out.stdout.decode("utf-8")


def main():
    args = arg_parser()
    if args.mode == "low":
        commands = phase_low_cov(
            args.vcf,
            args.out,
            args.thread,
            args.burn,
            args.prune,
            args.beagle,
            args.shapeit
        )
    elif args.mode == "normal":
        commands = phase_normal_cov(
            args.vcf,
            args.out,
            args.burn,
            args.prune,
            args.thread,
            args.shapeit
        )
    else:
        raise RuntimeError("Unknown phase mode")
    run_commands(commands)


if __name__ == '__main__':
    main()
