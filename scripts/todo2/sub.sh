
corrected=$1

subfasta=./sub.fasta
size=10000000
filesize=`ls -l $corrected | awk '{print $5}'`
echo $filesize
awk 'BEGIN{srand(); head=""} { if (/^>/) {head=$0} if (!/^>/) { if ("'$size'"/"'$filesize'">= rand() ) { print head; print $0 }}}' $corrected > $subfasta


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
