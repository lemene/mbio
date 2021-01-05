## BUSCO V3.0的脚本

    ` run_busco -i ../running/tomato/raven/polished-5.fasta -m geno  --cpu 40  -l  ./solanaceae_odb10  --offline -o contigs.busco --out_path raven`

    run_ctg () {
        name=$1
        run_busco -i ./ctgs/tomato-${name}-pilon5.fasta -m geno --cpu 40  -l  ../genelibs/solanales_odb10  -o $name -t $name
    }

## BUSCO V4的脚本
     busco -i contigs.fasta -m geno  --cpu 20  -l  ./enterobacterales_odb10  --offline -o contigs.busco --out_path aaa

## 采样fasta数据的脚本
corrected=$1

subfasta=./sub.fasta
size=10000000
filesize=`ls -l $corrected | awk '{print $5}'`
echo $filesize
awk 'BEGIN{srand(); head=""} { if (/^>/) {head=$0} if (!/^>/) { if ("'$size'"/"'$filesize'">= rand() ) { print head; print $0 }}}' $corrected > $subfasta


## 多次使用racon polish contig的脚本
contigs=$1
#reads=${@:2}
reads=$2

count=4
thread=46


workdir=polish
mkdir -p $workdir

rds=$reads
ctgs=$contigs

for ((i=0;i<$count;i++))
do
  time minimap2 -t $thread -x map-ont $ctgs $rds > $workdir/ol_$i.paf
  time racon -m 8 -x -6 -g -8 -w 500 -t $thread $rds $workdir/ol_$i.paf $ctgs  > $workdir/polished_$i.fasta
  ctgs=$workdir/polished_$i.fasta
done
