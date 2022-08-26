import os
import re
import sys

class SamItem:
    def __init__(self, line):
        its = line.split()
        self.qname = its[0]
        self.flag = int(its[1])
        self.rname = its[2]
        self.pos = int(its[3])
        self.map_quality = int(its[4])
        self.cigar = its[5]
        self.qseq = its[9];

    def found(self): 
        return (self.flag & 4) != 4 and (self.flag & 0x100) != 0x100

    def stat(self, refs):
        pattern = re.compile(r"(\d+)([MIDNSHP=X])")
        match, insert, delete, mismatch, cut, length = 0, 0, 0, 0, 0, len(self.qseq)
        ref = refs[self.rname] 
        qoff, roff = 0, self.pos-1

        for m in pattern.finditer(self.cigar):
            n, t = int(m.group(1)), m.group(2)

            if t == "M":
                for i in range(n):
                    if ref[roff+i] == self.qseq[qoff+i]:
                        match += 1
                    else:
                        mismatch += 1
                qoff += n
                roff += n
            elif t == "=":
                match += n
                qoff += n
                roff += n
            elif t == "X":
                mismatch += n
                qoff += n
                roff += n
            elif t == 'S':
                cut += n
                qoff += n
            elif t == 'H':
                cut += n
                length += n
                pass
            elif t == 'I':
                insert += n
                qoff += n
            elif t == 'D':
                delete += n
                roff += n
            else:
                assert False, "dfa"
        return match, insert, delete, mismatch, cut, length

    def overlap(self):
        pattern = re.compile(r"(\d+)([MIDNSHP=X])")
        match, insert, delete, mismatch, cut, length = 0, 0, 0, 0, 0, len(self.qseq)
        #ref = refs[self.rname] 
        qoff, roff = 0, 0
        state = 0
        head, tail = 0, 0
        for m in pattern.finditer(self.cigar):
            n, t = int(m.group(1)), m.group(2)

            if t == "M":
                qoff += n
                roff += n
            elif t == "=":
                qoff += n
                roff += n
            elif t == "X":
                qoff += n
                roff += n
            elif t == 'S':
                if state == 0: head += n
                if state == 1: tail += n
                #qoff += n
            elif t == 'H':
                if state == 0: head += n
                if state == 1: tail += n
            elif t == 'I':
                qoff += n
            elif t == 'D':
                roff += n
            else:
                assert False, "dfa"

            if t not in "HS":
               state = 1

        qstart, qend, qlen = head, head + qoff, head + qoff + tail
        rstart, rend = self.pos-1, self.pos - 1 + roff
        return qstart, qend, qlen, rstart, rend

def load_sam(fname):
    return [SamItem(line) for line in open(fname) if not line.startswith('@')]

def load_ref(fname):
    from Bio import SeqIO
    return {i.name : i.seq for i in SeqIO.parse(fname, "fasta") }

def stat_error(ref_fname, sam_fname):
    sam_items = load_sam(sam_fname)

    refs = load_ref(ref_fname)
    match, insert, delete, mismatch, cut, length = 0, 0, 0, 0, 0, 0
    for i in sam_items:
        if i.found():
            ss = i.stat(refs)
            match += ss[0]
            insert += ss[1]
            delete += ss[2]
            mismatch += ss[3]
            cut += ss[4]
            length += ss[5]
        else:
            cut += 0
           
    print(match, insert, delete, mismatch, cut, length)
    print(match/(length-cut), insert/(length-cut), delete/(length-cut), mismatch/(length-cut), cut/length)


def filter_sam(ifname, ofname):
    ofile = open(ofname, "w")
    max_overhang = 500
    rlen = 0
    for line in open(ifname):
        if not line.startswith("@"):
           item = SamItem(line)
           rlen = max(rlen, item.overlap()[-1])

          
    for line in open(ifname):
        if line.startswith("@"):
           ofile.write(line)
        else:
           item = SamItem(line)
           qstart, qend, qlen, rstart, rend,  = item.overlap()
           if rstart >=0 and (qstart <= max_overhang or rstart <= max_overhang) and \
              (qlen - qend <= max_overhang or rlen - rend <= max_overhang) and \
              qend - qstart >= 3000:
              print(qend, qstart)
              ofile.write(line)  

def usage(f, msg):
    print("Usage: %s %s %s" % (sys.argv[0], f.__name__, msg))

def filter_overhang(ifname, ofname, max_overhang=500):
    rlen = 0
    for line in open(ifname):
        if not line.startswith("@"):
           item = SamItem(line)
           rlen = max(rlen, item.overlap()[-1])
          
    ofile = open(ofname, "w")
    for line in open(ifname):
        if line.startswith("@"):
           ofile.write(line)
        else:
           item = SamItem(line)
           qstart, qend, qlen, rstart, rend,  = item.overlap()
           if rstart >=0 and (qstart <= max_overhang or rstart <= max_overhang) and \
              (qlen - qend <= max_overhang or rlen - rend <= max_overhang) :
              ofile.write(line)  

def sam_filter_overhang():
    if len(sys.argv) == 4 or len(sys.argv) == 5:
        ifname = sys.argv[2]
        ofname = sys.argv[3]
        max_overhang = int(sys.argv[4]) if len(sys.argv) >= 5 else 500
        filter_overhang(ifname, ofname, max_overhang)
    else:
        usage(sam_filter_overhang, "ifname(*.sam) ofname(*.sam) [max_overhang(500)]")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
       locals()[sys.argv[1]]()
    else:
       for func in list(locals().keys()):
           if func.startswith("sam_"):
               print(func)
