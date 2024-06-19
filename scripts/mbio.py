#!/usr/bin/env python3

import os, sys


#Setting executable paths
root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
sys.path.insert(0, root)
os.environ["PATH"] = root + os.pathsep + os.environ["PATH"]

import importlib
from mbio.utils.logger import logger

def main():
    tools = {
        "paf" : "mbio.ftype.paffile",
        "fx" : "mbio.fsa.fxbug",
        "mp" : "mbio.mproc",
        "rp" : "mbio.wrap.run_prog",
        "tb" : "mbio.ftype.table",
        "td" : "mbio.todo"
    }

    cmd = sys.argv[1].split("_")[0]

    if cmd in tools:
        m = importlib.import_module(tools[cmd])
        sys.exit(m.main())
    else:
        logger.error("No cmd: %s" % sys.argv[1])

if __name__ == "__main__":
    main()