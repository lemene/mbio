
'''存放pbsim工具相关的脚本'''

import sys, os
import argparse

import mbio.utils.utils as utils


def iterate_maf_line(fname):
    s = [0, None, None]
    for line in open(fname):
        if s[0] == 0:
            if line[0] == 'a':
                s[0] = 1
        elif s[0] == 1:
            assert line[0] == 's'
            s[1] = line
            s[0] = 2
        elif s[0] == 2:
            assert line[0] == 's'
            s[2] = line
            s[0] = 0
            yield s[1],s[2]
    return

def iterate_maf(fname):
    '''
a
s NC_001133.9 Saccharomyces cerevisiae S288C chromosome I, complete sequence 31612 10834 + 230218 CTTC-T--G-...
s S1_1      0 11554 +  11554 CTTCTTGC...
'''
    s = [0, None, None]
    for line in open(fname):
        if s[0] == 0:
            if line[0] == 'a':
                s[0] = 1
        elif s[0] == 1:
            assert line[0] == 's'
            its = line.split()
            s[1] = its
            s[0] = 2
        elif s[0] == 2:
            assert line[0] == 's'
            its = line.split()
            s[2] = its
            s[0] = 0
            query = s[2][1], int(s[2][5]), int(s[2][2]), int(s[2][3]), s[2][6]
            m = s[1].index("+")
            target = s[1][1], int(s[1][m+1]), int(s[1][m-2]), int(s[1][m-2])+int(s[1][m-1]), s[1][m+2]
            yield query, target, s[2][4]

    return

def pbsim_to_paf(argv):
    '''将maf文件转成paf文件
       pbsim_to_paf maf-fname [paf-fname]
'''

    try:
        ifname = sys.argv[2]
        ofname = ofname = sys.argv[3] if len(sys.argv) >= 4 else ifname + ".paf"

        def to_paf(ref, read):
            # add read
            its = [None]*12
            its[0], its[1], its[2], its[3], its[4]  = read[1], read[5], read[2], read[3], read[4]
            m = ref.index('+')
            assert m != -1
            its[5], its[6], its[7], its[8] = ref[1], ref[m+1], ref[m-2], str(int(ref[m-2]) + int(ref[m-1]))

            assert len(read[6]) == len(ref[m+2])
            its[9] = str(sum([1 for a, b in zip(read[6], ref[m+2]) if a == b]))
            its[10] = ref[m+1]
            its[11] = "60"

            return its

        ofile = open(ofname, "w")
        status = [0, None, None]
        for line in open(ifname):
            if status[0] == 0:
                if line[0] == 'a':
                    status[0] = 1
            elif status[0] == 1:
                assert line[0] == 's'
                its = line.split()
                status[1] = its
                status[0] = 2
            elif status[0] == 2:
                assert line[0] == 's'
                its = line.split()
                status[2] = its
                ofile.write("\t".join(to_paf(status[1], status[2])))
                ofile.write("\n")
                status[0] = 0

        assert status[0] == 0
    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(pbsim_to_paf.__doc__)
        

# PBSIM_PATH=~/tool/PBSIM-PacBio-Simulator
# ref=$1
# reads=$2
# tmp=__tmp__
# $PBSIM_PATH/src/pbsim --prefix $tmp --depth 100 --length-max 65000 --model_qc $PBSIM_PATH/data/model_qc_clr --length-mean 14000 --accuracy-mean 0.85 $ref
# cat $tmp*.fastq > $reads.fastq
# cat $tmp*.maf > $reads.maf
# rm $tmp*.fastq $tmp*.maf $tmp*.ref
def pbsim_run():
    '''运行pbsim，生成模拟数据
    pbsim_run ref reads
'''
    try:
        ref = sys.argv[2]
        reads = sys.argv[3]
        binpath = "~/tool/PBSIM-PacBio-Simulator"
        tmpname = "__tmp__"

        parser = argparse.ArgumentParser()
        parser.add_argument("--depth", type=int, default=100)
        parser.add_argument("--accuracy", type=float, default=0.85)
        parser.add_argument("--sd", type=float, default=0.02)
        args = parser.parse_args(sys.argv[4:])

        depth = args.depth
        accuracy = args.accuracy
        sd = args.sd

        cmds = "{binpath}/src/pbsim --prefix {tmpname} --depth {depth} --length-max 65000 --model_qc {binpath}/data/model_qc_clr --length-mean 14000 --accuracy-mean {accuracy} --accuracy-sd {sd} {ref}".format(
            binpath=binpath, tmpname=tmpname, depth=depth, accuracy=accuracy, sd=sd, ref=ref
        )
        print(cmds)
        os.system(cmds)
        cmds = "cat {tmpname}*.fastq > {reads}.fastq".format(tmpname=tmpname, reads=reads)
        print(cmds)
        os.system(cmds)
        cmds = "cat {tmpname}*.maf > {reads}.maf".format(tmpname=tmpname, reads=reads)
        print(cmds)
        os.system(cmds)

        cmds = "rm {tmpname}*.fastq {tmpname}*.maf {tmpname}*.ref".format(tmpname=tmpname)
        print(cmds)
        os.system(cmds)

    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(pbsim_run.__doc__)


def pbsim_verify_refmap():
    '''验证refmap的比对结果
    pbsim_verify_refmap target query
'''
    try:
        tfname = sys.argv[2]
        qfname = sys.argv[3]

        target = {}
        #for line in open(tfname):
        #    its = line.split()
        #    target[its[0]] = [its[5], its[4], int(its[7]), int(its[8])]

        for i in iterate_maf(tfname):
            target[i[0][0]] = (i[1][0], i[2], i[1][2],i[1][3]) # name direct start end

        query = {}
        for line in open(qfname):
            its = line.split()
            if its[0] not in query or not query[its[0]]:
                tr = target[its[0]]

                loc = False
                if its[5] == tr[0] and its[4] == tr[1]:
                    ql, qs, qe = int(its[1]), int(its[2]), int(its[3])
                    ts, te = int(its[7]), int(its[8])
                    if its[4] == '+':
                        ts -= qs
                        te += ql - qe
                    else:
                        ts -= ql - qe
                        te += qs

                    loc = abs(ts - tr[2]) < 1000
                query[its[0]] = loc

        print(sum([1 for k, v in query.items() if v]))
        print(sum([1 for k, v in query.items() if not v]))
        print(len(query), len(target))
        #for k, v in  query.items():
        #    if not v:
        #        print(k)

    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(pbsim_verify_refmap.__doc__)


def pbsim_filter_maf():
    '''过滤maf文件的部分数据
    pbsim_filter_map ifname ofname reserved
'''
    try:
        ifname = sys.argv[2]
        ofname = sys.argv[3]
        reversed_fname = sys.argv[4]
        reversed = set([line.split()[0] for line in open(reversed_fname)])

        ofile = open(ofname, "w")
        for its in iterate_maf_line(ifname):
            n = its[1].split()[1]
            if n in reversed:
                ofile.write("a\n%s%s\n" % (its[0], its[1]))

    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(pbsim_filter_maf.__doc__)

def pbsim_test():
    try:
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--depth", type=int, default=100)
        args = parser.parse_args(sys.argv[2:])
        print(args.depth)
    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(pbsim_test.__doc__)

        


_local_func = locals()
def main():
    utils.script_entry(sys.argv, _local_func, "pbsim_")

if __name__ == '__main__':
    main()







