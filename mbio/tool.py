import os

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
        r = os.system(cmd)
        if reqsucc: assert r == 0

def run(cmd, reqsucc=True):
    r = os.system(cmd)
    if reqsucc: assert r == 0


def newer(f0, f1):
    return not os.path.lexists(f1) or os.path.getmtime(f0) > os.path.getmtime(f1)
