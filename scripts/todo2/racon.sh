last_contigs=$1
reads=$2
threads=$3
N=$4


minimap2_bin=~/tool/minimap2-2.10/minimap2
racon_bin=~/tool/racon-1.3.1/build/bin/racon

workdir=`pwd`

for ((i=1; i<=$N; ++i));
do
    echo Start racon $i: $(date "+%Y-%m-%d %H:%M:%S")
    polished=$workdir/$i/polished.fasta

    if [ "$polished" -ot "$last_contigs" ]; then
        mkdir -p $i && cd $i
        $minimap2_bin -x map-ont -t $threads $last_contigs $reads > rd2ctg.paf
        $racon_bin -t $threads $reads rd2ctg.paf $last_contigs > polished.fasta
        cd -
    fi
    echo End racon $i: $(date "+%Y-%m-%d %H:%M:%S")
    last_contigs=$polished
done


# bash racon.sh `pwd`/../human/6-bridge_contigs/polished_contigs.fasta `pwd`/../../data/rawreads.fastq 40 4