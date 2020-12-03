#!/usr/bin/env python3

'''评估各类数据的质量'''

import os, sys
import traceback
import argparse

prjdir = os.path.sep.join([os.path.dirname(os.path.abspath(__file__)), ".."])
sys.path.append(prjdir)

import mbio.tool as tl

def eval_contig_accuracy(argv):
    '''调用pomoxis的asscess_assembly程序评估assembly的质量
    eval_contig_accuracy contigs [ref(./ref.fna) [threads[10]]]
'''
    parser = argparse.ArgumentParser("调用pomoxis的asscess_assembly程序评估assembly的质量")
    parser.add_argument("--reference", type=str, default="./ref.fna")
    parser.add_argument("--threads", type=int, default=10)
    parser.add_argument("contigs", type=str)

    try:
        args = parser.parse_args(argv)
        ctgs = args.contigs
        ref = args.reference
        threads = args.threads

        cmd = "assess_assembly -t %d -r %s -i %s" % (threads, ref, ctgs)
        os.system(cmd)
    except:
        traceback.print_exc()


def get_this_script_folder():
    folder, _ = os.path.split(__file__)
    return folder


def eval_read_accuracy(argv):
    '''评估reads的准确度，首先对reads采样（100M），然后使用minimap2(--eqx)比对到ref上，最后评估错误率。
'''
    
    parser = argparse.ArgumentParser();
    try:

        reads = argv[0]
        stub = argv[1]
        ref = "./ref.fna"

        workdir = "__wrkdir"
        if not os.path.exists(workdir): os.mkdir(workdir)

        name, _ = os.path.splitext(os.path.split(reads)[1])
        sample_size = 100000000
        subreads = "%s/%s-%dM.fasta" % (workdir, name, sample_size/1000000)
        rd2ref = "%s/%s-rd2ref.paf" % (workdir, name)
        result = "%s/%s-%s" % (workdir, name, stub)

        cmd = "python3 %s/read.py rd_sample random %s %s %d" % (get_this_script_folder(), reads, subreads, sample_size)
        tl.run_if_modified([reads], [subreads], cmd)

        cmd = "minimap2 -x asm20 -t 40 %s %s -c --eqx > %s" % (ref, subreads, rd2ref)
        tl.run_if_modified([subreads, ref], [rd2ref], cmd)

        cmd = "python3 %s/paffile.py paf_accuracy %s 2>&1 | tee %s" % (get_this_script_folder(), rd2ref, result)
        print(cmd)
        tl.run_if_modified([rd2ref], [result], cmd)
        os.system("cat %s" % result)

    except:
        traceback.print_exc()
        print("----------------")
        print(eval_read_accuracy.__doc__)


if __name__ == '__main__':
    if len(sys.argv) > 1:
       locals()[sys.argv[1]](sys.argv[2:])
    else:
       for func in list(locals().keys()):
           if func.startswith("eval_"):
               print("%s: %s" % (func, locals()[func].__doc__.split("\n")[0]))