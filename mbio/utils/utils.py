import os

from mbio.utils.logger import logger

mydir, _ = os.path.split(__file__)
prjdir = os.path.join(mydir, "..", "..")

def run_if_modified(ifiles, ofiles, cmd, force=False, reqsucc=True):
    '''如果ofiles修改时间落后ifiles，则运行func'''

    print(ifiles)
    print(ofiles)
    # 使支持单文件
    _ifiles = [ifiles] if type(ifiles) == str else ifiles
    _ofiles = [ofiles] if type(ofiles) == str else ofiles

    itimes =[ os.path.getmtime(f) for f in _ifiles]
    otimes = [os.path.getmtime(f) if os.path.lexists(f) else 0 for f in _ofiles]

    if len(otimes) == 0 or max(itimes) > min(otimes) or force:
        logger.info("run: %s", cmd)
        r = os.system(cmd)
        if reqsucc: assert r == 0

def run(cmd, reqsucc=True):
    r = os.system(cmd)
    if reqsucc: assert r == 0


def newer(f0, f1):
    return not os.path.lexists(f1) or os.path.getmtime(f0) > os.path.getmtime(f1)


def open_readable_file(fname):
    if fname == "-":
        return sys.stdin
    elif fname.endswith(".gz"):
        return gzip.open(fname, "rt") 
    else:
        return open(fname, "r")

def open_writeable_file(fname):
    if fname == "-":
        return sys.stdout
    elif fname.endswith(".gz"):
        return gzip.open(fname, "wt") 
    else:
        return open(fname, "w")
    
def script_entry(argv, locals, prefix):
    
    if len(argv) > 1:
        locals[argv[1]](argv[2:])
    else:
        maxlen = max([len(func) for func in list(locals.keys())])
        for func in sorted(list(locals.keys())):
            if func.startswith(prefix):
                doc = locals[func].__doc__
                print("%s%s: %s" % (func, " "*(maxlen-len(func)), doc.split("\n")[0] if doc != None else ""))