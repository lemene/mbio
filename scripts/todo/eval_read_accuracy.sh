# 评估reads的准确率
# 使用minimap2将reads比对到ref，再使用paf_accuracy评估。
# 需要修改reads和ref的路径。

mbio=~/work/mbio
ref=../../data/reference.fna
#org_reads=../ecoli/1-correct/0/corrected_reads_0.fasta

tempdir=tempdir
name=$1
stub=$2

org_reads=$name.fasta

reads=./$tempdir/${name}-reads_100M.fasta

overlaps=./$tempdir/${name}-rd2ref.paf
result=./result/${name}-${stub}

mkdir -p $tempdir result

# sample
if [ $org_reads -nt $reads ]; then
   python3 $mbio/script/read.py rd_sample random $org_reads $reads 100000000
fi



if [ $reads -nt $overlaps ]; then
   minimap2 -x asm20 -t 40 $ref $reads -c --eqx > $overlaps
fi

if [ $overlaps -nt $result ]; then
   python3 $mbio/script/paffile.py paf_accuracy $overlaps 2>&1 | tee $result
else
   cat $result
fi
