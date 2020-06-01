
ref1=../../../data/sk1.fa
ref2=../../../data/y12.fa
reads= ../../yeast/1-correct/0/corrected_reads_0.fasta

k=15
outdir=eval_${k}_result

name1=${ref1##*/}
name2=${ref2##*/}

if [ $ref1 -nt $outdir/$name1.tsv ]; then
  jellyfish count -C -m $k -s 1000000000 $threads $ref1 -o $outdir/$name1.jf
  jellyfish dump -c -t $outdir/$name1.jf > $outdir/$name1.tsv
fi


if [ $ref2 -nt $outdir/$name2.tsv ]; then
  jellyfish count -C -m $k -s 1000000000 $threads $ref2 -o $outdir/$name2.jf
  jellyfish dump -c -t $outdir/$name2.jf > $outdir/$name2.tsv
fi


python3 ~/work/mbio/script/eval_diploid.py edi_build $ref1
~
~
~
~
~
~
~
~
~
