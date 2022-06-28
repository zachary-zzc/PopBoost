# file format transform
convert ped2dgm MergedVariants.ped MergedVariants.dgm

# generate dgm commands by run_ohana.sh script
# base command:
#   1. qpas MergedVariants.dgm -k <k> -qo q.matrix -fo f.matrix -mi 5
#   2. nemeco MergedVariants.dgm f.matrix -co c.matrix -mi 5
#   3. convert cov2nwk c.matrix tree.nwk
#   4. convert nwk2svg tree.nwk tree.svg
# gen_qpas.sh will auto detect experiment repeat time by k

## in gen_ohana.sh we set the start k from 2 to 13
## this will generate output at:
##  1. ./K${k}/$k.rep$rep.qmatrix
##  2. ./K${k}/$k.rep$rep.fmatrix
##  3. ./K${k}/$k/rep$rep.cmatrix
##  4. ./K${k}/$k/rep$rep.nwk
##  5. ./K${k}/$k/rep$rep.svg

bash gen_ohana.sh MergedVariants.dgm ./ > run.sh  # generate command
bash run.sh  # run command
