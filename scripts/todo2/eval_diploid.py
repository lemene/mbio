'''计算reads或contigs包含父本或母本的kmer数目，评估reads或contigs的switch错误
eval_dipolid_kmer ref1 ref2 reads/ctgs k
'''

import os, sys
import multiprocessing as mp
import traceback
from Bio import SeqIO
import math
import functools
import operator
import gzip


THREADS = 20

def file_mtime (file):
    return os.stat(file).st_mtime

def file_newer(file1, file2):
    if type(file1) == str and type(file2) == str:
        return not os.path.exists(file2) or file_mtime(file1) >= file_mtime(file2)
    elif type(file1) == list and type(file2) == str:
        r = False
        for f in file1:
            r = not os.path.exists(file2) or file_mtime(f) >= file_mtime(file2)
            if r: break
        return r
    else:
        assert 0, "type of file is not str or list[str]"



def split_fname(fname):
    p, name = os.path.split(fname)
    m, ext = os.path.splitext(name) 
    return p, m, ext

def count_ref_kmer(klen, refs):

    result = []
    for ref in refs:
        path, name, ext = split_fname(ref)   
        if not os.path.exists(path + "/kmer") : os.makedirs(path + "/kmer");

        ofile = path + "/kmer/" + name + "_" + str(klen) 
        if file_newer(ref, ofile+".tsv"):

            print(ofile)
            cmd = "jellyfish count -C -m %d -s 1000000000 -t %d %s -o %s" % (klen, THREADS, ref,  ofile+".jf")
            print(cmd)
            os.system(cmd)
            cmd = "jellyfish dump -c -t %s > %s" % (ofile+".jf", ofile+ ".tsv")
            print(cmd)
            os.system(cmd)
        result.append(ofile+".tsv")
    return result
    
def load_kmers(fname):
    '''load xxx.tsv file'''
   
    kmers = set()
    for line in open(fname):
        kmers.add(line.split()[0])

    return kmers


def load_parent_kmers(father, mather):
    fkmer = load_kmers(father)
    mkmer = load_kmers(mather)

    return (fkmer - mkmer, mkmer - fkmer, fkmer & mkmer)

_m = {'A':'T','C':'G','G':'C','T':'A','a':'t','c':'g','g':'c','t':'a'}

def rv(kmer):
    return "".join([_m[i] for i in reversed(kmer)])    

def stat_read_kmer_worker(inputs, ouputs, kmers, k):
    def count(r):
        count = [r.name, 0, 0, 0, 0]
        for i in range(len(r.seq)-k+1):
            kmer = r.seq[i:i+k]
            vkmer = rv(kmer)
            if kmer in kmers[0] or vkmer in kmers[0]:
                count[1] += 1
            elif kmer in kmers[1] or vkmer in kmers[1]:
                count[2] += 1
            elif kmer in kmers[2] or  vkmer in kmers[2]:
                count[3] += 1
            else:
                count[4] += 1
        return count

    while True:
        rlist = inputs.get()
        if rlist != None:
            ouputs.put([count(r) for r in rlist])
            inputs.task_done()
        else:
            inputs.task_done()
            break

def stat_read_kmer(fname, kmers, k, nproc):

    inputs = mp.JoinableQueue();
    outputs = mp.Queue();

    procs = []
    for i in range(nproc):
        p = mp.Process(target=stat_read_kmer_worker, args=(inputs, outputs, kmers, k))
        p.start()
        procs.append(p);
    
    ## product
    fobj = gzip.open(fname, "rt") if fname.endswith('.gz') else open(fname);
    njob, reads = 0, []
    for i, r in enumerate(SeqIO.parse(fobj, "fasta")):
        reads.append(r)
        if len(reads) >= 1000:
            inputs.put(reads)
            njob += 1
            reads = []
    
    if len(reads) > 0:
        inputs.put(reads)
        njob += 1
        reads = []

    [inputs.put(None) for i in range(nproc)]

    inputs.join()

    result = []
    for i in range(njob):
        result += outputs.get()

    return result

def save_analyze_result(result, outfname):
    ofile = open(outfname, "w")

    for r in result:
       print(r)
       ofile.write("%s %d %d %d %d\n" % tuple(r))

    print(len(result))


def edi_build():
    try:
        refs = sys.argv[2:4]
        reads = sys.argv[4]
        k = int(sys.argv[5])

        _, name, ext = split_fname(reads)
        result_fname = "result_" + name
        ofiles = count_ref_kmer(k, refs)

        if file_newer(ofiles+[reads], result_fname):
            fkmer, mkmer, ckmer = load_parent_kmers(ofiles[0], ofiles[1])
            print(len(fkmer), len(mkmer), len(ckmer))
        
            result = stat_read_kmer(reads, [fkmer, mkmer, ckmer], k, 40)
            save_analyze_result(result, result_fname)       

        print(result_fname) 
    except:
        traceback.print_exc()
        print("------------")
        print(edi_build.__doc__)


def edi_result():
    '''给出结果的一些统计信息
    edi_result result
'''
    try:
        rfname = sys.argv[2]
        err = [0, 0, 0, 0, 0]  # err correct common unique all
        for line in open(rfname):
            its = line.split()
            kc = [int(i) for i in its[1:]]  # col cvi coomon abnormal 

            err[0] += min(kc[0], kc[1])
            err[1] += max(kc[0], kc[1])
            err[2] += kc[2]
            err[3] += kc[3]
            err[4] += sum(kc)
        print(err)
        print("%.06f %.06f %.06f %.06f " % (err[0]/err[-1], err[1]/err[-1], err[2]/err[-1], err[3]/err[-1]))
    except:
        traceback.print_exc()
        print("------------")
        print(edi_result.__doc__)

def edi_eval_ignore():
    '''分析ignore的正确率'''
    try:
        ifname = sys.argv[2]
        point = int(sys.argv[3])

        count = [0, 0]
        for line in open(ifname):
            its = line.split()
            a0, a1 = int(its[0]), int(its[1])
            count[0] += 1

            if a0 < point and a1 >= point or a0 >= point and a1 < point:
                count[1] += 1
        print(count, count[1]/count[0])
    except:
        traceback.print_exc()
        print("------------")
        print(__doc__)

if __name__ == '__main__':
    if len(sys.argv) > 1:
       locals()[sys.argv[1]]()
    else:
       for func in list(locals().keys()):
           if func.startswith("edi_"):
               print("%s: %s" % (func, locals()[func].__doc__))