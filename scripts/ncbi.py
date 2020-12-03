import sys, os
import urllib.request, re
import logging

def get_srrlist_from_sxr(sxr):
    url = "https://www.ncbi.nlm.nih.gov/sra/"
    pattern = re.compile(r'<a href="//trace.ncbi.nlm.nih.gov/Traces/sra/\?run=(SRR.*?)">')

    req = urllib.request.urlopen(url + sxr)
    html = req.read().decode('utf-8')
    return [it.group(1) for it in pattern.finditer(html)]

def get_baxh5_from_srr(srr):
    url = "https://trace.ncbi.nlm.nih.gov/Traces/sra/?run=" 
    pattern = re.compile(r'<a href="(https.*?ba[xs].h5.*?)">')

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

def save_sra_download_file(fname, sralist):
    ofile = open(fname, "w")
    for srr, sra in sralist:
        ofile.write("# " + srr + "\n")
        ofile.write("wget -c %s\n" % sra)


def ncbi_download_sra():
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

def ncbi_download_baxh5():
    '''根据数据的SXR号，下载对应的bax.h5文件
    ncbi_download_baxh5 sxr
'''
    try:

        srx = sys.argv[2]

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("baxh5")

        logger.info("Get SRR from " + srx)
        srrlist = get_srrlist_from_sxr(srx)
        save_list("srrlist", srrlist)

        logger.info("Get baxh5 from " + str(srrlist))
        baxh5 = [[srr, get_baxh5_from_srr(srr)] for srr in srrlist]
        save_baxh5_download_file("download.sh", baxh5)

        
        logger.info("Start running download.sh")
        #os.system("bash download.sh")

        logger.info("End downloading baxh5")

    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(ncbi_download_baxh5.__doc__)

if __name__ == '__main__':
    if len(sys.argv) > 1:
       locals()[sys.argv[1]]()
    else:
       for func in list(locals().keys()):
           if func.startswith("ncbi_"):
               print("%s: %s" % (func, locals()[func].__doc__.split("\n")[0]))
