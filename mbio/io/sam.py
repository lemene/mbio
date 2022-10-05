'''读写sam文件'''

import re

CIGAR = r"(\d+)([MIDNSHP=X])"

CIGAR_RE = re.compile(CIGAR)


class SamIter(object):
    def __init__(self, samname):
        self.sam = open(samname)

    def __iter__(self): return self

    def __next__(self):
        for line in self.sam:
            if line[0] == '@':
                continue
            qname, flag, rname, pos, mapq, cigar, rnext, pnext, tlen, seq, qual, *others = line.split()

            opt = {}
            for o in others:
                items = o.split(':')
                assert len(items) == 3
                if items[1] == 'i':
                    opt[items[0]] = int(items[2])
                else:
                    opt[items[0]] = items[2]

            return qname, int(flag), rname, int(pos), mapq, cigar, rnext, int(pnext), int(tlen), seq, qual, opt

        else:
            raise StopIteration


def split_line(line):
    qname, flag, rname, pos, mapq, cigar, rnext, pnext, tlen, seq, qual, *others = line.split()

    opt = {}
    for o in others:
        items = o.split(':')
        assert len(items) == 3
        if items[1] == 'i':
            opt[items[0]] = int(items[2])
        else:
            opt[items[0]] = items[2]

    return qname, int(flag), rname, int(pos), mapq, cigar, rnext, int(pnext), int(tlen), seq, qual, opt


def get_cigar_len(cigar):
    '''计算cigar所暗含的长度'''
    qlen, rlen, hlen, slen = 0, 0, 0, 0
    for m in CIGAR_RE.finditer(cigar):
        n, t = int(m.group(1)), m.group(2)
        if t in "M=X":
            qlen += n
            rlen += n

        elif t == 'S':
            slen += n
        elif t == 'H':
            hlen += n
        elif t == 'I':
            qlen += n
        elif t == 'D':
            rlen += n

    return qlen, rlen, hlen, slen


def sample(ifname, ofname, percent):
    '''对sam文件的进行采样，只使用其percent的数据'''
    percent = int(percent)

    import random

    area100 = range(100)
    ofile = open(ofname, "w")
    for line in open(ifname):
        if line[0] == '@':
            ofile.write(line)
        else:
            if random.sample(area100, 1)[0] < percent:
                ofile.write(line)


def filter_sam(ifname, ofname, filterfunc=lambda x: True):

    ofile = open(ofname, "w")
    for line in open(ifname):
        if line[0] == '@':
            ofile.write(line)
        else:
            if filterfunc(split_line(line)):
                ofile.write(line)

class CigarIter(object):
    def __init__(self, cigar):
        self.inner_iter = CIGAR_RE.finditer(cigar)
        self.ref = 0
        self.query = 0

    def __iter__(self): return self

    def __next__(self):
        for m in self.inner_iter:
            n, t = int(m.group(1)), m.group(2)
            ref, query = self.ref, self.query

            if t in "HS":
                self.query += n
            elif t in "M=X":
                self.ref += n
                self.query += n
            elif t == 'I':
                self.query += n
            elif t == 'D':
                self.ref += n
            else:
                assert False, "bad type:%s" % t

            return t, n, query, ref

        else:
            raise StopIteration

def cigar_summary(cigar):
    '''计算匹配各个位置
        refstart: 匹配到ref的起始位置
        对cigar的格式顺序有如下假定：[硬修剪] [软修剪] 其它 [软修剪] [硬修剪]
    '''
    clips = [0, 0, 0, 0] # [hclip, sclip, sclip, hclip]
    reflen, inlen, dellen = 0, 0, 0

    state = 0 #  0 硬修剪 1 软修剪 2 其它 2 软修剪 3 硬修剪 4

    for m in CIGAR_RE.finditer(cigar):
        n, t = int(m.group(1)), m.group(2)
        if t == 'H':
            if state == 0:
                clips[0] = n
                state = 1
            elif state == 2 or state == 3:
                clips[3] = n
                state = 4
            else:
                assert False, "cigar，%s出现的位置与假定不符" % t

        elif t in "S":
            if state == 0 or state == 1:
                clips[1] = n
                state = 2
            elif state == 2:
                clips[2] = n
                state = 3
            else:
                assert False, "cigar，%s出现的位置与假定不符" % t
        else:
            if state == 0 or state == 1:
                state = 2
            elif state == 2:
                pass    # 合法状态，不需要处理
            else:
                assert False, "cigar，%s出现的位置与假定不符" % t

            if t in "M=X":
                reflen += n
            elif t == 'I':
                inlen += n
            elif t == 'D':
                reflen += n
                dellen += n
            else:
                assert False, "cigar，未能识别字符：%s" % t

    return reflen, inlen, dellen, clips

if __name__ == '__main__':
    import sys
    result = locals()[sys.argv[1]](*sys.argv[2:])
    print(result)
