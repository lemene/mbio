#!/usr/bin/env python3
 
import sys
import traceback
import gzip
from Bio import SeqIO
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("read.py")

def open_read_file(fname, mode="r"):
    if fname[-6:] == ".fasta":
        return open(fname, mode), "fasta"
    if fname[-4:] == ".fna":
        return open(fname, mode), "fasta"
    elif fname[-6:] == ".fastq":
        return open(fname, mode), "fastq"
    elif fname[-9:] == ".fasta.gz":
        return gzip.open(fname, mode+"t"), "fasta"
    elif fname[-9:] == ".fastq.gz":
        return gzip.open(fname, mode+"t"), "fastq"
    else:
        return None, ""


def sample_random(ifname, ofname, base_size):
    from Bio import SeqIO
    import random    

    ifile, iftype = open_read_file(ifname)

    total_base_size = 0
    for i, rec in enumerate(SeqIO.parse(ifile, iftype)):
        total_base_size += len(rec.seq)

    ratio = (base_size*1.2) / total_base_size   # 1.2 多采样0.5
    
    ifile.seek(0);
    allrec = [] 
    for i, rec in enumerate(SeqIO.parse(ifile, iftype)):
        if random.random() <= ratio:
            allrec.append(rec)

    random.shuffle(allrec)

    accu = 0
    ofile, oftype = open_read_file(ofname, "w")
    for r in allrec:
        SeqIO.write(r, ofile, oftype)
        accu += len(r.seq)
        if accu >= base_size: break


def sample_longest(ifname, ofname, base_size):
    from Bio import SeqIO
    import heapq

    assert ifname[-6:] == ".fasta" or ifname[-6:] == ".fastq"
    assert ofname[-6:] == ".fasta" or ofname[-6:] == ".fastq"

    accu = 0
    allrec = []
    for i, rec in enumerate(SeqIO.parse(ifname, ifname[-5:])):
        if accu < base_size or allrec[0][0] < len(rec.seq):
            accu += len(rec.seq)
            heapq.heappush(allrec, [len(rec.seq), i, rec])

        while accu - allrec[0][0] >= base_size:
            accu -= allrec[0][0]
            heapq.heappop(allrec)


    with open(ofname, "w") as ofile:
        for r in allrec:
            SeqIO.write(r[2], ofile, ofname[-5:])


def sample_min_length(ifname, ofname, min_length):
    from Bio import SeqIO
    import heapq

    assert ifname[-6:] == ".fasta" or ifname[-6:] == ".fastq"
    assert ofname[-6:] == ".fasta" or ofname[-6:] == ".fastq"

    with open(ofname, "w") as ofile:
        for i, rec in enumerate(SeqIO.parse(ifname, ifname[-5:])):
            if len(rec.seq) >= min_length:

                SeqIO.write(rec, ofile, ofname[-5:])




def rd_sample():
    """Usage: extract reads from fasta or fastq file
    random ifnane ofname basesize
    longest ifname ofname basesize
    min_length ifname ofname min_length """

    try:
        method = sys.argv[2]
        ifname = sys.argv[3]
        ofname = sys.argv[4]
        if method == "random":
            base_size = eval(sys.argv[5])
            sample_random(ifname, ofname, base_size)
        elif method == "longest":
            base_size = eval(sys.argv[5])
            sample_longest(ifname, ofname, base_size)
        elif method == "min_length":
            min_length = eval(sys.argv[5])
            sample_min_length(ifname, ofname, min_length)
        else:
            assert False

    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(rd_sample.__doc__)


usage_rd_check_dup_name = """Usage:
    ifname"""

def rd_check_dup_name():
    """检查文件的read是否有重名"""
    try:
        ifname = sys.argv[2]
        names = set()
        from Bio import SeqIO
        for i, rec in enumerate(SeqIO.parse(ifname, ifname[-5:])):
            if rec.name in names:
                print(rec.name)
            else:
                names.add(rec.name)
    except:
        print(usage_rd_check_dup_name)

def rd_rename_dup_name(argv):
    '''命名重名reads'''
    parser = argparse.ArgumentParser(rd_rename_dup_name.__doc__)

    parser.add_argument("ifname", type=str)
    parser.add_argument("ofname", type=str)
    try:
        from collections import defaultdict
        from Bio import SeqIO
        args = parser.parse_args(argv)

        ifile, itype = open_read_file(args.ifname, "r")
        ofile, otype = open_read_file(args.ofname, "w")

        names = defaultdict(int)


        for i, rec in enumerate(SeqIO.parse(ifile, itype)):
            names[rec.id] += 1
            if names[rec.id] > 1:
                rec.id = rec.id + "_" + str(names[rec.id]-1)
                #TODO rec.description 会重复rec.id
                SeqIO.write(rec, ofile, otype)
    except:
        traceback.print_exc()
        print("-----------------")
        parser.print_usage()
        

def rd_remove_dup_name(argv):
    '''删除重名reads'''
    parser = argparse.ArgumentParser(rd_remove_dup_name.__doc__)

    parser.add_argument("ifname", type=str)
    parser.add_argument("ofname", type=str)
    try:
        from collections import defaultdict
        from Bio import SeqIO
        args = parser.parse_args(argv)

        ifile, itype = open_read_file(args.ifname, "r")
        ofile, otype = open_read_file(args.ofname, "w")

        names = defaultdict(int)

        for i, rec in enumerate(SeqIO.parse(ifile, itype)):
            names[rec.id] += 1
            if names[rec.id] == 1:
                SeqIO.write(rec, ofile, otype)

    except:
        traceback.print_exc()
        print("-----------------")
        parser.print_usage()
    
def rd_remove_empty(argv):
    '''删除空的reads'''
    
    parser = argparse.ArgumentParser(rd_remove_empty.__doc__)

    parser.add_argument("ifname", type=str)
    parser.add_argument("ofname", type=str)
    try:
        args = parser.parse_args(argv)

        ifile, itype = open_read_file(args.ifname, "r")
        ofile, otype = open_read_file(args.ofname, "w")
        for i, rec in enumerate(SeqIO.parse(ifile, itype)):
            if len(rec.seq) > 0:
                SeqIO.write(rec, ofile, otype)

    except:
        traceback.print_exc()
        print("-----------------")
        parser.print_usage()

def rd_split():
    """将fasta分割成小块"""

    try:
        ifname = sys.argv[2]
        odir = sys.argv[3]

        from Bio import SeqIO

        assert ifname[-6:] == ".fasta" or ifname[-6:] == ".fastq"

        for i, rec in enumerate(SeqIO.parse(ifname, ifname[-5:])):
            ofname = odir + "/" + rec.name + ifname[-6:]
            with open(ofname, "w") as ofile:
                SeqIO.write(rec, ofile, ofname[-5:])
        
    except:
        print(rd_split.__doc__)

def rd_show():
    """显示reads的片段
rd_show fname name xxx-yyy
"""

    try:
        ifname = sys.argv[2]
        name = sys.argv[3]
        ranges = sys.argv[4].split("-");
        ranges = [eval(i) for i in ranges]

        from Bio import SeqIO

        assert ifname[-6:] == ".fasta" or ifname[-6:] == ".fastq"

        for i, rec in enumerate(SeqIO.parse(ifname, ifname[-5:])):
            if rec.name == name:
                print(rec.seq[ranges[0]:ranges[1]])
            
    except:
        print(rd_show.__doc__)

def rd_name_len(argv):
    '''输出reads名称和长度'''

    
    try:
        ifname = argv[0]

        ifile, iftype = open_read_file(ifname)

        total_base_size = 0
        for i, rec in enumerate(SeqIO.parse(ifile, iftype)):
            print(rec.name, len(rec.seq))

    except:
        print(rd_name_len.__doc__)

        
def rd_run_length():
    '''将read安装run-length方式编码'''

    try:
        ifname = sys.argv[2]
        ofname = sys.argv[3]
        lofname = sys.argv[4]

        ifile, iftype = open_read_file(ifname)

        ofile = open(ofname, "w")
        lofile = open(lofname, "w")
        for i, rec in enumerate(SeqIO.parse(ifile, iftype)):
            bases = []
            lens = []
            for b in rec.seq:
                if len(bases) == 0 or bases[-1] != b:
                    lens.append(1)
                    bases.append(b)
                else:
                    lens[-1] += 1
            ofile.write(">%s\n%s\n" % (rec.name, "".join(bases)))
            lofile.write(">%s\n%s\n" % (rec.name, ",".join([str(i) for i in lens])))
    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(rd_run_length.__doc__)
        
def rd_test_kmer():
    try:
        ifname = sys.argv[2]
        klen = int(sys.argv[3])
        rd0 = sys.argv[4]
        rd1 = sys.argv[5]

        ifile, iftype = open_read_file(ifname)
        rec0, rec1 = None, None
        for i, rec in enumerate(SeqIO.parse(ifile, iftype)):
 
            if type(rec0) == type(None) and rec.name == rd0:
                rec0 = rec
            if type(rec1) == type(None) and rec.name == rd1:
                rec1 = rec
            if type(rec0) != type(None) and rec1 != type(None):
                break

        def kmers(s, k):
            return set([s[i:i+k] for i in range(0, len(s)-k+1)])

        kmers0 = kmers(rec0.seq, klen)
        kmers1 = kmers(rec1.seq, klen)

        print(rec0.name, rec1.name)

        print(len(kmers0 & kmers1), len(kmers0 | kmers1), len(kmers0),len(kmers1))
    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(rd_test_kmer.__doc__)
        

def rd_diff():
    '''求两个reads的差集, a - b = c
    rd_diff afname bfname cfname
'''
    try:
        afname = sys.argv[2]
        bfname = sys.argv[3]
        cfname = sys.argv[4]

        afile, aftype = open_read_file(afname)
        bfile, bftype = open_read_file(bfname)

        bnames = set()
        for rec in SeqIO.parse(bfile, bftype):
            bnames.add(rec.name)

        cfile, cftype = open_read_file(cfname, "w")
        for rec in SeqIO.parse(afile, aftype):
            if rec.name not in bnames:
                SeqIO.write(rec, cfile, cftype)
    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(rd_diff.__doc__)


def rd_pacbio_head():
    '''将fasta的头部改为pacbio模式，daligner需要'''
    try:
        ifname = sys.argv[2]
        ofname = sys.argv[3]

        ofile = open(ofname, "w")
        for line in open(ifname):
            if line[0] == '>':
                its = line.split()
                its[0] = its[0]+"/0/0_1"
                line_new = " ".join(its)
                ofile.write("%s\n" % line_new)
            else:
                ofile.write(line)

    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(rd_pacbio_head.__doc__)

if __name__ == '__main__':
    if len(sys.argv) > 1:
       locals()[sys.argv[1]](sys.argv[2:])
    else:
       for func in list(locals().keys()):
           if func.startswith("rd_"):
               print("%s: %s" % (func, locals()[func].__doc__.split("\n")[0]))
