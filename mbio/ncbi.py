import sys, os
import urllib.request, re
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ncbi")
def get_srrlist_from_sxr(sxr):
    url = "https://www.ncbi.nlm.nih.gov/sra/"
    pattern = re.compile(r'<a href="//trace.ncbi.nlm.nih.gov/Traces/sra/\?run=(SRR.*?)">')

    req = urllib.request.urlopen(url + sxr)
    html = req.read().decode('utf-8')
    return [it.group(1) for it in pattern.finditer(html)]

def get_baxh5_from_srr(srr):
    url = "https://trace.ncbi.nlm.nih.gov/Traces/sra/?run=" 
    pattern = re.compile(r'<a href="(https.*?ba[xs].h5.*?)">')


    logger.info(url+srr)
    req = urllib.request.urlopen(url+srr)
    html = req.read().decode('utf-8')
    return [it.group(1) for it in pattern.finditer(html)]

    
def get_bam_from_srr(srr):
    url = "https://trace.ncbi.nlm.nih.gov/Traces/sra/?run=" 
    pattern = re.compile(r'<a href="(https.*?bam.*?)">')

    req = urllib.request.urlopen(url+srr)
    html = req.read().decode('utf-8')
    return [it.group(1) for it in pattern.finditer(html)]

def get_sra_from_srr(srr):
    url = "https://trace.ncbi.nlm.nih.gov/Traces/sra/?run=" 
    print(r'<a href="(https://sra-download.*?ncbi.nlm.nih.gov/.*?%s.*?%s.*?)">' % (srr, srr))
    pattern = re.compile(r'<a href="(https://sra-download.*?ncbi.nlm.nih.gov/.*?%s.*?%s.*?)">' % (srr, srr))

    req = urllib.request.urlopen(url+srr)
    html = req.read().decode('utf-8')
    return [it.group(1) for it in pattern.finditer(html)][0]

def save_list(fname, lst):
    ofile = open(fname, "w")
    [ofile.write("%s\n" % i) for i in lst]

def save_baxh5_download_file(fname, baxh5):
    ofile = open(fname, "w")
    for srr, h5 in baxh5:
        ofile.write("# " + srr + "\n")
        for f in h5:
            if f.find("bax.h5") != -1:
                ofile.write("wget -c %s\n" % f)
            else:
                ofile.write("# wget -c %s\n" % f)

def save_bam_download_file(fname, bam):
    ofile = open(fname, "w")
    for srr, fs in bam:
        ofile.write("# " + srr + "\n")
        for f in fs:
            ofile.write("wget -c %s\n" % f)

def save_sra_download_file(fname, sralist):
    ofile = open(fname, "w")
    for srr, sra in sralist:
        ofile.write("# " + srr + "\n")
        ofile.write("wget -c %s\n" % sra)


def ncbi_download_sra(argv):
    '''根据数据的SXR号，下载对应的bax.h5文件
    ncbi_download_baxh5 sxr
'''
    try:

        srx = sys.argv[2]

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("sra")

        logger.info("Get SRR from " + srx)
        srrlist = get_srrlist_from_sxr(srx)
        save_list("srrlist", srrlist)

        logger.info("Get sra from " + str(srrlist))
        sralist = [[srr, get_sra_from_srr(srr)] for srr in srrlist]
        save_sra_download_file("download.sh", sralist)

        
        logger.info("Start running download.sh")
        #os.system("bash download.sh")

        #logger.info("End downloading baxh5")

    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(ncbi_download_sra.__doc__)

def ncbi_download_baxh5(argv):
    '''根据数据的SXR号，下载对应的bax.h5文件
'''
    parser = argparse.ArgumentParser("下载baxh5")
    parser.add_argument("--srr", type=str, default="")
    parser.add_argument("--srrlist", type=str, default="")
    parser.add_argument("--dlcmds", type=str, default="dl-baxh5.sh")
    parser.add_argument("--failed", type=str, default="failed")
    try:

        args = parser.parse_args(argv)
        srr = args.srr
        srrlist = args.srrlist
        dlcmds = args.dlcmds
        failed = args.failed

        assert(srr == "" and srrlist != "" or srr != "" and srrlist == "")

        srrs = [srr] if srr != "" else [i.strip() for i in open(srrlist)]
        logger.info("srr size = %d" % len(srrs))

        logger.info("get baxh5")
        baxh5 = [[s, get_baxh5_from_srr(s)] for s in srrs]
        
        failed_srrs = []
        logger.info("check baxh5")
        for k, v in baxh5:
            if len(v) != 4:
                failed_srrs.append(k)

        save_baxh5_download_file(dlcmds, baxh5)

        with open(failed, "w") as f:
            for i in failed_srrs:
                f.write("%s\n" % i)
        
    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(ncbi_download_baxh5.__doc__)


def ncbi_download_bam(argv):
    '''根据数据的SXR号，下载对应的bax.h5文件
'''
    parser = argparse.ArgumentParser("下载bam文件")
    parser.add_argument("--srr", type=str, default="")
    parser.add_argument("--srrlist", type=str, default="")
    parser.add_argument("--dlcmds", type=str, default="dl-baxh5.sh")
    parser.add_argument("--failed", type=str, default="failed")
    try:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("baxh5")

        args = parser.parse_args(argv)
        srr = args.srr
        srrlist = args.srrlist
        dlcmds = args.dlcmds
        failed = args.failed

        assert(srr == "" and srrlist != "" or srr != "" and srrlist == "")

        srrs = [srr] if srr != "" else [i.strip() for i in open(srrlist)]
        logger.info("srr size = %d" % len(srrs))

        logger.info("get bam")
        baxh5 = [[s, get_bam_from_srr(s)] for s in srrs]
        
        failed_srrs = []
        logger.info("check baxh5")
        for k, v in baxh5:
            if len(v) != 1:
                failed_srrs.append(k)

        save_bam_download_file(dlcmds, baxh5)

        with open(failed, "w") as f:
            for i in failed_srrs:
                f.write("%s\n" % i)
        
    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(ncbi_download_baxh5.__doc__)

if __name__ == '__main__':
    if len(sys.argv) > 1:
       locals()[sys.argv[1]](sys.argv[2:])
    else:
       for func in list(locals().keys()):
           if func.startswith("ncbi_"):
               print("%s: %s" % (func, locals()[func].__doc__.split("\n")[0]))
