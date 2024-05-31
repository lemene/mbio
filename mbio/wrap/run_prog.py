#! /usr/bin/env python3

from pydoc import describe
import sys, os
import traceback
import argparse
import glob
import multiprocessing as mp
from collections import defaultdict
import logging

import mbio.utils.utils as utils
import mbio.utils.logger as logger
tl = utils

mydir, _ = os.path.split(__file__)

prjdir = os.path.sep.join([os.path.dirname(os.path.abspath(__file__)), ".."])
sys.path.append(prjdir)

def rp_sam4igv(argv):
    '''将sam文件处理成igv可显示的格式, 生成xxx.sorted.bam xxx.sorted.bam.bai
'''
    parser = argparse.ArgumentParser(rp_sam4igv.__doc__)
    parser.add_argument("sam", type=str)
    parser.add_argument("--filter", type=int, default=1)

    try:
        args = parser.parse_args(argv)

        assert args.sam.endswith(".sam")

        samfname = args.sam
        if args.filter:
            samfname = args.sam.replace(".sam", ".flt.sam")
            cmd = "python3 %s/../samfile.py sam_filter_overhang %s %s" % (mydir, args.sam, samfname)
            tl.run_if_modified(args.sam, samfname, cmd)


        name = samfname[:-4]


        cmd = "samtools view -bS %s > %s.bam" % (samfname, name)
        tl.run_if_modified(samfname, name + ".bam", cmd)

        cmd = "samtools sort %s.bam -o %s.sorted.bam" % (name, name)
        tl.run_if_modified(name + ".bam", name + ".sorted.bam", cmd)

        cmd = "samtools index %s.sorted.bam" % name
        tl.run_if_modified(name + ".sorted.bam", name + ".sorted.bam.bai", cmd)

        tl.run("rm -f %s.bam" % name)
    except:
        traceback.print_exc()
        print("----------------")
        print(rp_sam4igv.__doc__)


def rp_mecat_cns(argv):
    '''调用mecat纠错raw reads
'''

    '''
if [ -z $1 ] ; then
   echo Usage: mecat_correction rawreads
   exit 1
fi

rawreads=$1
threads=20
mecat2pw -j 0 -d $rawreads -o rawreads.pm.can -w wrk_dir -t $threads
mecat2cns -i 0 -t $threads rawreads.pm.can $rawreads corrected.fasta
'''

    try:
        rawreads = argv[0]
        cnsreads = argv[1]
        threads = int(argv[2]) if len(argv) >= 3 else 4

        pm = "rawreads.pm.can"
        
        cmd = "mecat2pw -j 0 -d %s -o %s -w wrk_dir -t %d" % (rawreads, pm, threads)
        tl.run_if_modified([rawreads], [pm], cmd)

        cmd = "mecat2cns -i 0 -t %d %s %s %s" % (threads, pm, rawreads, cnsreads)
        tl.run_if_modified([pm], [cnsreads], cmd)

        tl.run("rm -rf %s* wrk_dir" % pm)
    except:
        traceback.print_exc()
        print("----------------")
        print(rp_mecat_cns.__doc__)


def rp_miniasm(argv):
    '''调用minimap2+miniasm完成组装
'''
    # minimap + miniasm
    try:
        reads = argv[0]
        contigs = argv[1]
        threads = argv[2]
        minimap2_options = argv[2]

        overlaps = "__overlaps.paf"
        graph = "__graph.gfa"
        cmd = f"minimap2 -t {threads} {minimap2_options} {reads} {reads} | gzip -1 > {overlaps}"
        tl.run_if_modified([reads], [overlaps], cmd)

        cmd = f"miniasm -f {reads} {overlaps} > {graph}"
        tl.run_if_modified([reads, overlaps], [graph], cmd)

        # awk '/^S/{print ">"$2"\n"$3}' $graph > $contigs
        cmd = f"""awk '/^S/{{print ">"$2"\n"$3}}' {graph} > {contigs}"""
        tl.run_if_modified([graph], [contigs], cmd)

        tl.run(f"rm -f {overlaps} {graph}")
    except:
        traceback.print_exc()
        print("----------------")
        print(rp_miniasm.__doc__)

def extract(f):
    fo = f.replace(".", "_")
    cmd = '''dextract -o%s.fasta -e"ln>=500" %s''' % (fo, f)
    print(cmd)
    os.system(cmd)

def extract(f):
    fo = f.replace(".", "_")
    #cmd = '''dextract -o%s.fasta -e"ln>=500" %s''' % (fo, f)
    cmd = '''pls2fasta -fastq %s %s.fastq -minSubreadLength 2000 -minReadScore 750 -trimByRegion''' % (f, f)
    print(cmd)
    os.system(cmd)

def rp_bax2fasta(argv):

    # enter the folder that contain *.bax.h5, and run bax2fasta.sh
    try:
        files = argv[0]
 

        with mp.Pool(10) as p:
            p.map(extract, glob.glob(files))
    
    except:
        traceback.print_exc()
        print("----------------")
        print(rp_bax2fasta.__doc__)
    '''
idx=1
for file in `echo *.bax.h5`
do
  dextract -orawreads${idx}.fasta -e"ln>=1000" $file
  idx=`expr $idx + 1`
done

'''

def rp_racon(argv):
    '''调用minimap2和racon完成polish
    rp_racon contigs reads polished [threads(4)] [minimap2_options(-x map-pb)] [racon_options()]
'''

    try:
        contigs = argv[0]
        reads = argv[1]
        polished = argv[2]
        threads = int(argv[3]) if len(argv) >= 4 else 4
        minimap2_options = argv[4] if len(argv) >= 5 else "-x map-pb"
        racon_options = argv[5] if len(argv) >= 6 else ""

        rd2ctg = "__rd2ctg__.paf"

        cmd = "minimap2 %s -t %d %s %s > %s" % (minimap2_options, threads, contigs, reads, rd2ctg)
        tl.run_if_modified([contigs, reads], [rd2ctg], cmd)

        cmd = "racon %s -t %d %s %s %s > %s" % (racon_options, threads, reads, rd2ctg, contigs, polished)
        print(cmd)
        tl.run_if_modified([reads, contigs, rd2ctg], [polished], cmd)

        #tl.run("rm -f " + rd2ctg)

    except:
        traceback.print_exc()
        print("----------------")
        print(rp_racon.__doc__)

# pbsim
#pbsim --prefix xxx --depth 20 --length-max 65000 --model_qc ~/tool/PBSIM-PacBio-Simulator/data/model_qc_clr  --length-mean 14000 --accuracy-mean 0.85 <reference.fasta>
def rp_pbsim():
    pass

# mummerplot
#$1=ref, $2=contigs
#nucmer  -l 100 -c 1000 -d 10 --banded -D 5 $1 $2
#delta-filter -i 95 -o 95 out.delta> out.best.delta
#mummerplot out.best.delta --fat -f -png
# ---------------
#    nucmer  -l 100 -c 1000 -d 10 --banded -D 5 $1 $2
#delta-filter -i 95 -o 95 out.delta > out.best.delta
#dnadiff -d out.best.delta
#mummerplot out.best.delta --fat -f -png
def rp_mummerplot(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=str)
    parser.add_argument("contigs", type=str)

    try:
        args = parser.parse_args(argv)
        contigs = args.contigs
        refs = args.reference

        cmd = f"nucmer  -l 100 -c 1000 -d 10 --banded -D 5 {refs} {contigs}"
        tl.run_if_modified([], [], cmd)

        cmd = f"delta-filter -i 95 -o 95 out.delta > out.best.delta"
        tl.run_if_modified([], [], cmd)

        cmd = f"dnadiff -d out.best.delta"
        tl.run_if_modified([], [], cmd)

        cmd = f"mummerplot out.best.delta --fat -f -png"
        tl.run_if_modified([], [], cmd)

        #tl.run("rm -f ")

    except:
        traceback.print_exc()
        print("----------------")
        print(rp_racon.__doc__)

def rp_pilon(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("contigs", type=str)
    parser.add_argument("--bwa", type=str, default="bwa")
    parser.add_argument("--threads", type=int, default=20)

    try:
        args = parser.parse_args(argv)
        contigs = args.contigs
        reads = args.reads
        threads = args.threads

        cmd = "%s index %s" % (args.bwa, args.contigs)
        tl.run_if_modified([contigs], [], cmd)

    except:
        traceback.print_exc()
        print("----------------")
        print(parser.usage)




def rp_purge_dups(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument("reads", type=str)
    parser.add_argument("contigs", type=str)
    parser.add_argument("--threads", type=int, default=20)

    try:
        args = parser.parse_args(argv)
        contigs = args.contigs
        reads = args.reads
        threads = args.threads

        #cmd = f"minimap2 -xmap-pb {contigs} {reads} | gzip -c - > rd2ctg.paf.gz"
        cmd = "minimap2 -x map-pb -t %d %s %s | gzip -c - > rd2ctg.paf.gz" % (threads, contigs, reads)
        tl.run_if_modified([contigs, reads], ["rd2ctg.paf.gz"], cmd)

        cmd = "pbcstat rd2ctg.paf.gz"
        tl.run_if_modified(["rd2ctg.paf.gz"], ["PB.base.cov", "PB.stat"], cmd)

        cmd = "calcuts PB.stat > cutoffs 2>calcults.log"
        tl.run_if_modified(["PB.stat"], ["cutoffs"], cmd)

        _, name = os.path.split(contigs)
        split_contigs = name + ".split"

        #cmd = f"split_fa {contigs} > {split_contigs}"
        cmd = "split_fa %s > %s" % (contigs , split_contigs)
        tl.run_if_modified([contigs], [split_contigs], cmd)

        #cmd = f"minimap2 -xasm5 -DP {split_contigs} {split_contigs} | gzip -c - > ctg2ctg.paf.gz"
        cmd = "minimap2 -x asm20 -DP -t %d %s %s | gzip -c - > ctg2ctg.paf.gz" % (threads, split_contigs, split_contigs)
        tl.run_if_modified([split_contigs], ["ctg2ctg.paf.gz"], cmd)

        cmd = "purge_dups -2 -T cutoffs -c PB.base.cov ctg2ctg.paf.gz > dups.bed 2> purge_dups.log"
        tl.run_if_modified(["PB.base.cov", "ctg2ctg.paf.gz", "cutoffs"], ["dups.bed"], cmd)

        #cmd = f"get_seqs dups.bed {contigs}"
        cmd = "get_seqs dups.bed %s" % contigs
        tl.run_if_modified(["dups.bed", contigs], ["purged.fa"], cmd)
        
        #tl.run("rm -f ")

    except:
        pass
        #traceback.print_exc()
        #print("----------------")
        #print(parser.usage)

def rp_eval_reads(argv):
    '''evaluate reads accuracy'''
    parser = argparse.ArgumentParser(rp_eval_reads.__doc__)
    parser.add_argument("reads", type=str)
    parser.add_argument("reference", type=str)
    parser.add_argument("--base_size", type=str, default="0")
    parser.add_argument("--wrkdir", type=str, default="./wrkdir")
    parser.add_argument("--subreads", type=str, default="")
    parser.add_argument("--threads", type=int, default=20)

    try:
        args = parser.parse_args(argv)
        base_size = eval(args.base_size)
        print(base_size)
        utils.run("mkdir -p %s" % args.wrkdir)

        subreads = args.reads if base_size <= 0 else args.subreads
        if subreads == "":
            subreads = os.path.join(args.wrkdir, "subreads_%d.fasta" % (base_size))

        cmd = "~/work/fsa/build/bin/fsa_rd_tools random %s %s --base_size %d" % (args.reads, subreads, base_size)
        utils.run_if_modified([args.reads], [subreads], cmd)

        paf = os.path.join(args.wrkdir, "subreads_%d.paf" % (base_size))
        cmd = "minimap2 -c --eqx -t %d %s %s > %s" % (args.threads, args.reference, subreads, paf)
        utils.run_if_modified([subreads, args.reference], [paf], cmd)

        result = os.path.join(args.wrkdir, "result_%d" % (base_size))
        cmd = "python3 %s/paffile.py paf_accuracy %s > %s" % (mydir, paf, result)
        utils.run_if_modified(paf, result, cmd)

        utils.run("cat %s" % result)
    except:
        traceback.print_exc()
        print("----------------")
        print(parser.usage)


_local_func = locals()
def main():
    utils.script_entry(sys.argv, _local_func, "rp_")

if __name__ == '__main__':
    main()
