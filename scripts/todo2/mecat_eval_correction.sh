#!/bin/bash

# 从Mecat论文的supplementary Note5 摘抄

if [ -z "$1" -o -z "$2" ]; then
    echo Usage: mecat_eval_correction corrected_reads size reference
    exit 1
fi 

corrected=$1
size=$2
reference=$3

subfasta=./sub.$size.fasta

if [ ! -f $subfasta ]; then
  basesize=`awk '{if (!/^>/) { k += length($0);}} END{print k;}' $corrected`
  #filesize=`ls -l $corrected | awk '{print $5}'`
  awk 'BEGIN{srand(); head=""} { if (/^>/) {head=$0} if (!/^>/) { if ("'$size'"/"'$basesize'">= rand() ) { print head; print $0 }}}' $corrected > $subfasta
fi

#evaluate


if [ ! -f eval1.$size.mcoords ]; then
  nucmer --maxmatch -p eval0.$size $reference $subfasta -t 20
  #nucmer --maxmatch -p eval0.$size $reference $subfasta 
  dnadiff -p eval1.$size -d eval0.$size.delta 
fi

# report
R --slave <<EOF
input = read.table("eval1.$size.mcoords")

uc = unique(input[,13])

reads_len=0 ; 
avg_cor=0
for ( i in 1: length(uc)) { 
    tmp = input[input[,13] == uc[i],]
    #if(length(tmp)>13) {
    if(length(tmp)>=13) {
        max_indx=which.max(as.numeric(tmp[,11]))
        reads_len = reads_len +as.numeric(tmp[max_indx,6])
        avg_cor = avg_cor +as.numeric(tmp[max_indx,7]) 
    } else { 
        reads_len = reads_len +as.numeric(tmp[,6])
        avg_cor = avg_cor +as.numeric(tmp[,7]) 
    }
}
print(reads_len)
print(avg_cor/length(uc))
EOF

