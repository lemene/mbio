import sys,os

def load_col_items(fname, p):
    items = []
    for line in open(fname):
        its = line.split()
        items.append(its[p])
    return items

def tb_intersect():
    try:
        fname0 = sys.argv[2]
        fname1 = sys.argv[3]


        items0 = set(load_col_items(fname0, 0))
        items1 = set(load_col_items(fname1, 0))


        for i in items0 & items1:
            print(i)
    except:

        import traceback
        traceback.print_exc()
        print(tb_intersect.__doc__)


def tb_diff():
    try:
        fname0 = sys.argv[2]
        fname1 = sys.argv[3]


        items0 = set(load_col_items(fname0, 0))
        items1 = set(load_col_items(fname1, 0))


        for i in items0 - items1:
            print(i)
    except:

        import traceback
        traceback.print_exc()
        print(tb_intersect.__doc__)
       
if __name__ == '__main__':
    if len(sys.argv) > 1:
       locals()[sys.argv[1]]()
    else:
       for func in list(locals().keys()):
           if func.startswith("tb_"):
               print("%s: %s" % (func, locals()[func].__doc__.split("\n")[0]))
