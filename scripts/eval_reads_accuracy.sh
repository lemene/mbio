# 提取部分reads，计算它的正确率
#
mbio=~/work/mbio
ref=./ref.fna
#org_reads=../ecoli/1-correct/0/corrected_reads_0.fasta

tempdir=tempdir
name=$1
stub=$2

org_reads=$name.fasta
reads=$org_reads
#reads=./$tempdir/${name}-reads_100M.fasta

overlaps=./$tempdir/${name}-rd2ref.paf
result=./result/${name}-${stub}

mkdir -p $tempdir result

# sample
if [ $org_reads -nt $reads ]; then
   python3 $mbio/scripts/read.py rd_sample random $org_reads $reads 100000000
fi



if [ $reads -nt $overlaps ]; then
   minimap2 -x asm20 -t 40 $ref $reads -c --eqx > $overlaps
fi

if [ $overlaps -nt $result ]; then
   python3 $mbio/scripts/paffile.py paf_accuracy $overlaps 2>&1 | tee $result
else
   cat $result
fi
