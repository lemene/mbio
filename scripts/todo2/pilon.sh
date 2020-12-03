set -e
contigs="`pwd`/tomato-wtdbg2.fasta"
threads=40

count=5

for i in `seq 1  $count`; do
   mkdir $i -p && cd $i
   if [ ! -f "polished.fasta" ]; then
       bash -x ../../run_pilon.sh $contigs $threads polished
   fi
   contigs=`pwd`"/polished.fasta"
   cd -
   echo $i
done

set -e
#contigs=../assembly.fasta
contigs=$1
threads=$2
polished=$3

bwa_bin=~/tool/bwa/bwa
samtools_bin=~/tool/samtools/samtools
pilon_bin=~/tool/pilon-1.22.jar


do_sam() {
  id=$1
  $bwa_bin aln -t $threads -f SpnLY-PF55-MS01-01-${id}_S1_L001_R1_001.fastq.sai $contigs /home/niefan/store/tomato/seq0/SpnLY-PF55-MS01-01-${id}_S1_L001_R1_001.fastq
  $bwa_bin aln -t $threads -f SpnLY-PF55-MS01-01-${id}_S1_L001_R2_001.fastq.sai $contigs /home/niefan/store/tomato/seq0/SpnLY-PF55-MS01-01-${id}_S1_L001_R2_001.fastq
  $bwa_bin sampe -f overlaps-$id.sam $contigs SpnLY-PF55-MS01-01-${id}_S1_L001_R1_001.fastq.sai SpnLY-PF55-MS01-01-${id}_S1_L001_R2_001.fastq.sai /home/niefan/store/tomato/seq0/SpnLY-PF55-MS01-01-${id}_S1_L001_R1_001.fastq /home/niefan/store/tomato/seq0/SpnLY-PF55-MS01-01-${id}_S1_L001_R2_001.fastq

  $samtools_bin view -bS overlaps-$id.sam > overlaps-$id.bam
  $samtools_bin sort -o overlaps-$id.sorted.bam overlaps-$id.bam

}


$bwa_bin index $contigs

do_sam 1
do_sam 2
do_sam 3

$samtools_bin merge overlaps.sorted.bam overlaps-1.sorted.bam  overlaps-2.sorted.bam overlaps-3.sorted.bam
$samtools_bin index overlaps.sorted.bam
java -Xmx500g -jar $pilon_bin --genome $contigs --bam overlaps.sorted.bam --fix snps,indels,gaps --output $polished --vcf
