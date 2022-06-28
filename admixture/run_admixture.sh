# !/bin/bash

# admixture=/mnt/beta/USERS/zhaozc/tools/admixture/v1.3.0/admixture
admixture=~/package/bin/admixture
max_likelihood_script=get_admixture_maxlikelihood.py;

bfile=${1:-null};
workdir=${2:-null};
startk=${3:-2};
endk=${4:-13};
reptime=${5:-10};

if [ ! -e $bfile.bed ] || [ ! -e $bfile.bim ] || [ ! -e $bfile.bim ]; then
    echo "missing entire bed file";
    echo "bash $0 bfile workdir startk[2] endk[13] reptime[10]";
    exit 1
fi

if [ $workdir = "null" ]; then
    echo "missing working directory";
    echo "bash $0 bfile workdir startk[2] endk[13] reptime[10]";
    exit 1
fi

if [ -e $workdir ]; then rm -r $workdir; fi
mkdir -p $workdir

# get workdir absolute path
workdir="$(cd $workdir; pwd -P)"

# working directory
if [ -e $workdir/cmds ]; then rm -r $workdir/cmds; fi
if [ -e $workdir/rep_files ]; then rm -r $workdir/rep_files; fi
if [ -e $workdir/results ]; then rm -r $workdir/results; fi
mkdir -p $workdir/cmds;
mkdir -p $workdir/rep_files;
mkdir -p $workdir/results/logs;

# get absolute path
base=`basename $bfile`
path="$(cd "$(dirname "$bfile")"; pwd -P)"

for ((k=startk; k<=endk; k++)); do
    for ((i=1; i<=reptime; i++)); do
        # generate link files
        ln -s $path/$base.bed $workdir/rep_files/K$k.rep$i.$base.bed;
        ln -s $path/$base.bim $workdir/rep_files/K$k.rep$i.$base.bim;
        ln -s $path/$base.fam $workdir/rep_files/K$k.rep$i.$base.fam;
        # generate command line
        echo "$admixture -j4 -s time --cv $workdir/rep_files/K$k.rep$i.$base.bed $k &> $workdir/results/logs/K$k.rep$i.log && echo done" >> $workdir/cmds/run_admixture.sh;
    done
done

# split and qsub
taskno=5;
lineno=`python -c "import math; print(math.ceil($(cat $workdir/cmds/run_admixture.sh | wc -l) / $taskno))"`
mkdir -p $workdir/cmds/run_admixture.sh.qsub
shuf $workdir/cmds/run_admixture.sh | split -l $lineno - $workdir/cmds/run_admixture.sh.qsub/run_admixture.

# enter qsub dir
curdir=`pwd -P`
cd $workdir/cmds/run_admixture.sh.qsub/
for f in $workdir/cmds/run_admixture.sh.qsub/run_admixture.*; do
    # qsub -cwd -V -q beta.q -l h_vmem=5G $f;
    submit $f;
done
cd $curdir

# prepare clumpak input
cd $workdir;

# create dir
mkdir -p results/Qmatrix;
mkdir -p results/Pmatrix;
mkdir -p results/selected;

# mv Qmatrix & Pmatrix from cmds folder
mv cmds/run_admixture.sh.qsub/*.Q results/Qmatrix;
mv cmds/run_admixture.sh.qsub/*.P results/Pmatrix;

# get the maximum likelihood rep from log files
for (( k = startk; k <= endk; k ++ )); do
    file=""
    for f in results/logs/K$k.*.log; do
        file="$file $f";
    done
    maxlog=`python3 $max_likelihood_script $file`;
    maxbase=`basename $maxlog | cut -f1,2 -d "."`;
    cp results/Qmatrix/$maxbase.*.Q results/selected/;
done

# zip
cd results/selected;
zip selected.zip *.Q;
cd ../Qmatrix;
for (( k = startk; k <= endk; k ++ )); do
    zip K$k.zip K$k.*.Q
done
zip allQ.zip *.zip

# mv zip file to workdir
cd ../
mv selected/selected.zip ../
mv Qmatrix/allQ.zip ../

# return to curdir
cd $cur_dir

