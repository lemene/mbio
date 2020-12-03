## BUSCO V3.0的脚本

    ` run_busco -i ../running/tomato/raven/polished-5.fasta -m geno  --cpu 40  -l  ./solanaceae_odb10  --offline -o contigs.busco --out_path raven`

    run_ctg () {
        name=$1
        run_busco -i ./ctgs/tomato-${name}-pilon5.fasta -m geno --cpu 40  -l  ../genelibs/solanales_odb10  -o $name -t $name
    }

## BUSCO V4的脚本
     busco -i contigs.fasta -m geno  --cpu 20  -l  ./enterobacterales_odb10  --offline -o contigs.busco --out_path aaa
