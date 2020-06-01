export PATH=~/niefan/tool/MECAT/Linux-amd64/bin:$PATH

name=ecoli
rawreads=
threads=16
genome_size=4800000
coverage=30

mecat2pw -j 0 -d $rawreads -o rawreads.pm.can -w wrk_dir -t $threads

mecat2cns -i 0 -t $threads rawreads.pm.can $rawreads corrected_rawreads

extract_sequences corrected_rawreads.fasta corrected_rawreads_${coverage}x.fasta $genome_size $coverage

mecat2canu -trim-assemble -p $name -d $name genomeSize=$genome_size ErrorRate=0.02 maxMemory=40 maxThreads=$threads useGrid=0 Overlapper=mecat2asmpw -pacbio-corrected corrected_rawreads_${coverage}x.fasta


ols=$1
id=$2
end=$3
idt=$4

if [ $3 -eq 0 ]; then
  awk '{ if ($3 >= "'$idt'" && ($1=="'$id'" && $6 <= 10 || $2 == "'$id'" && $10 <= 10 )) { print $0 }}' $ols
else
  awk '{ if ($3 >= "'$idt'" && ($1=="'$id'" && $8-$7 <= 10 || $2 == "'$id'" && $12-$11 <= 10 )) { print $0 }}' $ols
fi

ols=$1
id=$2
end=$3

if [ $3 -eq 0 ]; then
  awk '{ if ($1=="'$id'" && $6 <= 10 || $2 == "'$id'" && $10 <= 10 ) { print $0 }}' $ols
else
  awk '{ if ($1=="'$id'" && $8-$7 <= 10 || $2 == "'$id'" && $12-$11 <= 10 ) { print $0 }}' $ols
fi

ols=$1
id=$2
end=$3
idt=$4

if [ $3 -eq 0 ]; then
  awk '{ if ($10*100.0/$11 >= "'$idt'" && ($1=="'$id'" && $3 <= 10 || $6 == "'$id'" && $8 <= 10 )) { print $0 }}' $ols
else
  awk '{ if ($10*100.0/$11 >= "'$idt'" && ($1=="'$id'" && $2-$4 <= 10 || $6 == "'$id'" && $7-$9 <= 10 )) { print $0 }}' $ols
fi
