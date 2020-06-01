ref=$1
ctg=$2

nucmer --mum -l 100 -c 1000 -d 10 --banded -D 5 $ref $ctg
delta-filter -i 95 -o 95 out.delta > out.best.delta
dnadiff -d out.best.delta
mummerplot out.best.delta --fat -f --png


