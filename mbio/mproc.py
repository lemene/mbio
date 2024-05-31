import os, sys
import argparse
import multiprocessing as mp
import glob
import traceback

import mbio.utils.utils as utils
from mbio.utils.logger import logger


    
def grep_file(params):
    fn, pattern, option = params
    cmd = "grep %s %s %s" % (option, pattern, fn)
    logger.info("run %s" % cmd)
    output = os.popen(cmd).read()
    return output

def mp_grep(argv):
    parser = argparse.ArgumentParser("Running grep in multiple processes")
    parser.add_argument("files", type=str, default='')
    parser.add_argument("pattern", type=str, default='')
    parser.add_argument("--threads", type=int, default=10)
    parser.add_argument("--options", type=str, default="")
   
    try:
        args = parser.parse_args(argv)
        # get ols

        with mp.Pool(args.threads) as pool:
            params = [(fn, args.pattern, args.options) for fn in glob.glob(args.files)]
            result = pool.map(grep_file, params)
                
            for r in result:
                print(r, end="")                       

    except:
        traceback.print_exc()
        print("-----------------")
        parser.print_usage()

_local_func = locals()
def main():
    utils.script_entry(sys.argv, _local_func, "mp_")

if __name__ == '__main__':
    main()
