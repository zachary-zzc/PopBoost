input=$1
outdir=$2

dirname=`dirname $input`
basename=`basename $input`
ext=${basename##*.}
fname=$(basename $basename "."$ext)

name=""
if [ $ext = "lgm" ]; then
    ~/package/ohana/bin/convert bgl2lgm $dirname/$fname.bgl $dirname/$fname.lgm
    name=$fname.lgm
fi
if [ $ext = "dgm" ]; then
    name=$fname.dgm
fi

for k in 2 3;do
    mkdir -p $outdir/K$k
    for rep in $(seq 3);do
        echo "~/package/ohana/bin/qpas $dirname/$name -k $k -qo $outdir/K$k/$k.rep$rep.qmatrix -fo $outdir/K$k/$k.rep$rep.fmatrix -mi 100"
        echo "~/package/ohana/bin/nemeco $dirname/$name $outdir/K$k/$k.rep$rep.fmatrix -co $outdir/K$k/$k.rep$rep.cmatrix -mi 100"
        echo "~/package/ohana/bin/convert cov2nwk $outdir/K$k/$k.rep$rep.cmatrix $outdir/K$k/$k.rep$rep.nwk"
        echo "~/package/ohana/bin/convert nwk2svg $outdir/K$k/$k.rep$rep.nwk $outdir/K$k/$k.rep$rep.svg"
    done
done

for k in 4 5;do
    mkdir -p $outdir/K$k
    for rep in $(seq 5);do
        echo "~/package/ohana/bin/qpas $dirname/$name -k $k -qo $outdir/K$k/$k.rep$rep.qmatrix -fo $outdir/K$k/$k.rep$rep.fmatrix -mi 200"
        echo "~/package/ohana/bin/nemeco $dirname/$name $outdir/K$k/$k.rep$rep.fmatrix -co $outdir/K$k/$k.rep$rep.cmatrix -mi 200"
        echo "~/package/ohana/bin/convert cov2nwk $outdir/K$k/$k.rep$rep.cmatrix $outdir/K$k/$k.rep$rep.nwk"
        echo "~/package/ohana/bin/convert nwk2svg $outdir/K$k/$k.rep$rep.nwk $outdir/K$k/$k.rep$rep.svg"
    done
done

for k in 6 7;do
    mkdir -p $outdir/K$k
    for rep in $(seq 10);do
        echo "~/package/ohana/bin/qpas $dirname/$name -k $k -qo $outdir/K$k/$k.rep$rep.qmatrix -fo $outdir/K$k/$k.rep$rep.fmatrix -mi 300"
        echo "~/package/ohana/bin/nemeco $dirname/$name $outdir/K$k/$k.rep$rep.fmatrix -co $outdir/K$k/$k.rep$rep.cmatrix -mi 300"
        echo "~/package/ohana/bin/convert cov2nwk $outdir/K$k/$k.rep$rep.cmatrix $outdir/K$k/$k.rep$rep.nwk"
        echo "~/package/ohana/bin/convert nwk2svg $outdir/K$k/$k.rep$rep.nwk $outdir/K$k/$k.rep$rep.svg"
    done
done

for k in 8 9;do
    mkdir -p $outdir/K$k
    for rep in $(seq 10);do
        echo "~/package/ohana/bin/qpas $dirname/$name -k $k -qo $outdir/K$k/$k.rep$rep.qmatrix -fo $outdir/K$k/$k.rep$rep.fmatrix -mi 400"
        echo "~/package/ohana/bin/nemeco $dirname/$name $outdir/K$k/$k.rep$rep.fmatrix -co $outdir/K$k/$k.rep$rep.cmatrix -mi 400"
        echo "~/package/ohana/bin/convert cov2nwk $outdir/K$k/$k.rep$rep.cmatrix $outdir/K$k/$k.rep$rep.nwk"
        echo "~/package/ohana/bin/convert nwk2svg $outdir/K$k/$k.rep$rep.nwk $outdir/K$k/$k.rep$rep.svg"
    done
done

for k in 10 11;do
    mkdir -p $outdir/K$k
    for rep in $(seq 10);do
        echo "~/package/ohana/bin/qpas $dirname/$name -k $k -qo $outdir/K$k/$k.rep$rep.qmatrix -fo $outdir/K$k/$k.rep$rep.fmatrix -mi 500"
        echo "~/package/ohana/bin/nemeco $dirname/$name $outdir/K$k/$k.rep$rep.fmatrix -co $outdir/K$k/$k.rep$rep.cmatrix -mi 500"
        echo "~/package/ohana/bin/convert cov2nwk $outdir/K$k/$k.rep$rep.cmatrix $outdir/K$k/$k.rep$rep.nwk"
        echo "~/package/ohana/bin/convert nwk2svg $outdir/K$k/$k.rep$rep.nwk $outdir/K$k/$k.rep$rep.svg"
    done
done

for k in 12 13;do
    mkdir -p $outdir/K$k
    for rep in $(seq 10);do
        echo "~/package/ohana/bin/qpas $dirname/$name -k $k -qo $outdir/K$k/$k.rep$rep.qmatrix -fo $outdir/K$k/$k.rep$rep.fmatrix -mi 600"
        echo "~/package/ohana/bin/nemeco $dirname/$name $outdir/K$k/$k.rep$rep.fmatrix -co $outdir/K$k/$k.rep$rep.cmatrix -mi 600"
        echo "~/package/ohana/bin/convert cov2nwk $outdir/K$k/$k.rep$rep.cmatrix $outdir/K$k/$k.rep$rep.nwk"
        echo "~/package/ohana/bin/convert nwk2svg $outdir/K$k/$k.rep$rep.nwk $outdir/K$k/$k.rep$rep.svg"
    done
done
