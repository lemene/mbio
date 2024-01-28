#!/usr/bin/python3
import sys,os
import traceback
import argparse
import glob

import utils
import logger


def awk_ol_m4():

    assert len(sys.argv) == 3 or len(sys.argv) == 4, sys.argv[0]+" fname xx0,xx1 [yy1,yy2]"

    l_ids = sys.argv[2].split(",")
    r_ids = sys.argv[3].split(",") if len(sys.argv) == 4 and len(sys.argv[3]) > 0 else l_ids

    cond = []
    cond.append("(" + "||".join(["$1=="+i for i in l_ids]) + ")")
    cond.append("(" + "||".join(["$2=="+i for i in r_ids]) + ")")

    if len(sys.argv) == 3 or len(sys.argv) == 4 and sys.argv[3] != "":
        cmd = "awk '{if ("+"&&".join(cond) + "){print $0}}' "  + sys.argv[1]
    else:
        cmd = "awk '{if ("+"||".join(cond) + "){print $0}}' "  + sys.argv[1]
    print(cmd)
    os.system(cmd)


def awk_ol_m4_parallel():


    # cat arab/arab/3-assembly/pm.m4 | parallel --pipe awk \'{s+=\$1} END {print s}\'

    assert len(sys.argv) == 3 or len(sys.argv) == 4, sys.argv[0]+" fname xx0,xx1 [yy1,yy2]"

    l_ids = sys.argv[2].split(",")
    r_ids = sys.argv[3].split(",") if len(sys.argv) == 4 and len(sys.argv[3]) > 0 else l_ids

    cond = []
    cond.append("\\(" + "\\|\\|".join(["\\$1=="+i for i in l_ids]) + "\\)")
    cond.append("\\(" + "\\|\\|".join(["\\$2=="+i for i in r_ids]) + "\\)")

    if len(sys.argv) == 3 or len(sys.argv) == 4 and sys.argv[3] != "":
        cmd = "cat " + sys.argv[1] + " | parallel --pipe " +  "awk \\'{if \\("+"\\&\\&".join(cond) + "\\){print \\$0}}\\' " 
    else:
        #cmd = "awk '{if ("+"||".join(cond) + "){print $0}}' "  + sys.argv[1]
        cmd = "cat " + sys.argv[1] + " | parallel --pipe " +  "awk \\'{if \\("+"\\|\\|".join(cond) + "\\){print \\$0}}\\' " 
    print(cmd)
    os.system(cmd)

def sh_awk_ol():
    '''sh_awk_ol_paf fname names(xx0,xx1,...) [ftype(paf|m4)]
'''
    try:
        fname = sys.argv[2]
        names = sys.argv[3].split(",")
        ftype = "paf" if len(sys.argv) < 5 else  sys.argv[4]

        pos0, pos1 = ("$1==", "$6==") if ftype == "paf" else ("$1==", "$2==")

        cond = "||".join(["".join([pos0, n, "||", pos1, n]) for n in names])

        cmd = "awk '{if (" + cond + "){print $0}}' " + fname if fname != "-" else ""
        #print(cmd)
        os.system(cmd)

    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(sh_awk_ol_paf.__doc__)

def grep_read():
    pattern = [r'"^>\(']
    for r in sys.argv[2:-1]:
        pattern.append(r"\<")
        pattern.append(r)
        pattern.append(r"\>")
        pattern.append(r"\|")
    
    pattern.append(r"\<")
    pattern.append(sys.argv[-1])
    pattern.append(r"\>")
    pattern.append(r'\)"')
    #print("".join(pattern))
    
    cmd = "grep -A1 " + "".join(pattern) + " " + sys.argv[1]
    print(cmd)
    os.system(cmd)

def sh_grep_subreads():
    '''从fasta文章中找出对应的reads，并按照名字生成文件
    sh_grep_subreads fname dir read0 read1 ...
'''

    try:
        ifname = sys.argv[2]
        dirname = sys.argv[3]
        rnames = sys.argv[4:]

        os.system("mkdir -p " + dirname);

        grepcmd = "zgrep" if ifname.endswith(".gz") else "grep"
        for rn in rnames:
            cmd = " ".join([grepcmd, "-A1", r'"^>\<%s\>"' % rn, ifname, ">", "%s/%s.fasta" % (dirname, rn)])

            print(cmd)
            os.system(cmd)

    except:
        traceback.print_exc()
        print("----------------")
        print(sh_grep_subreads.__doc__);


def grep_ol():

    cmd = ["grep "]
    
    p = []
    for i in sys.argv[2:]:
        p.append("\(\<" + i + "\>\)")

    s = "\(" + "\|".join(p) + "\)"
    
    cmd.append("\"^" + s + "\t" + s + "\"")
    cmd.append(sys.argv[1])
    
    print(" ".join(cmd))
    os.system(" ".join(cmd))

def grep_ol_0():
    
    cmd = ["grep "]
    
    p1 = r"\(^" + r"\(" + r"\|".join([i + r"\>" for i in sys.argv[2:]]) + r"\)\)"
    
    p2 = r"\(^[0-9]\+" + r"\(" + r"\|".join(["\t" + i + "\t"  for i in sys.argv[2:]]) + r"\)\)"
    
    cmd = "grep " + '"' + p1 + r"\|" + p2 + '" ' + sys.argv[1]
    cmd1 = "grep " + '"' + p1 + '" ' + sys.argv[1]
    cmd2 = "grep " + '"' + p2 + '" ' + sys.argv[1]
    

    os.system(cmd)



def sh_awk_mean():
    '''统计某列的平均值
    sh_awk_mean fname col
'''

    try:
        fname = "" if sys.argv[2] == '-' else sys.argv[2]
        col = int(sys.argv[3])

        cmd = "awk 'BEGIN {n=0;s=0} {n+=1; s+=$%d;} END{print(s/n)}' %s" % (col+1, fname)
        print(cmd)
        os.system(cmd)

    except:
        traceback.print_exc()
        print("----------------")
        print(sh_awk_mean.__doc__);


def sh_grep_overlap_by_name(argv):
    parser = argparse.ArgumentParser("使用grep命令找出overlaps包含的名字")
    parser.add_argument("overlaps", type=str)
    parser.add_argument("reads0", type=str)
    parser.add_argument("reads1", type=str, default="")

    try:
        args = parser.parse_args(argv)
        
        for f in glob.glob(args.overlaps):
            logger.logger.info(f)
            grep = 'zgrep' if f.endswith('.gz') else 'grep'

            reads0 = '\|'.join(args.reads0.split(','))
            reads1 = '' if args.reads1 == "" else '\|'.join(args.reads1.split(','))
            cmd = '%s -w "%s" %s | grep -w "%s"' % (grep, reads0, f, reads1)
            logger.logger.info(cmd)
            os.system(cmd)

    except:
        traceback.print_exc()
        print("-----------------")
        parser.print_usage()

if __name__ == '__main__':
    utils.script_entry(sys.argv, locals(), "sh_")
