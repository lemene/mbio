#!/usr/bin/env python3

import os
import sys


#Setting executable paths
root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
sys.path.insert(0, root)
os.environ["PATH"] = root + os.pathsep + os.environ["PATH"]

def main():
    cmd = sys.argv[1].split("_")[0]

    if cmd == "paf":
        from mbio.ftype.paffile import main
    elif cmd == "fx":
        from mbio.fsa.fxbug import main
    elif cmd == "mp":
        from mbio.mproc import main
    elif cmd == "rp":
        from mbio.wrap.run_prog import main
    elif cmd == "tb":
        from mbio.ftype.table import main
    else:
        pass
    sys.exit(main())

if __name__ == "__main__":
    main()